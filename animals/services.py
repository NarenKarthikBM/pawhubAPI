# your_app/services.py

import logging
from concurrent.futures import ThreadPoolExecutor

import requests
from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db.models import Case, F, FloatField, Func, Value, When
from pgvector.django import CosineDistance

from .models import Pet

logger = logging.getLogger(__name__)


class PetCreationService:
    """
    Orchestrates the creation of a pet profile by calling external AI/ML microservices.
    """

    def _call_gemini_service(self, image_url: str) -> dict | None:
        """Calls the external Gemini service to get breed details."""
        try:
            response = requests.post(
                settings.GEMINI_SERVICE_URL,
                json={"image_url": image_url},
                timeout=30,  # 30-second timeout
            )
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.RequestException as e:
            logger.error(f"🔴 Error calling Gemini service: {e}")
            return None

    def _call_embedding_service(self, image_url: str) -> dict | None:
        """Calls the external Embedding service to get the image vector."""
        try:
            response = requests.post(
                settings.EMBEDDING_SERVICE_URL,
                json={"image_url": image_url},
                timeout=45,  # Longer timeout as this involves model loading/inference
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"🔴 Error calling Embedding service: {e}")
            return None

    def process_pet_from_url(self, image_url: str) -> dict:
        """
        Processes a pet from an image URL by calling services concurrently.
        Returns a dictionary with all the data needed to create a Pet object.
        """
        gemini_result = None
        embedding_result = None

        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both tasks to the thread pool
            future_gemini = executor.submit(self._call_gemini_service, image_url)
            future_embedding = executor.submit(self._call_embedding_service, image_url)

            # Retrieve results
            gemini_result = future_gemini.result()
            embedding_result = future_embedding.result()

        # Consolidate results
        final_data = {
            "breed_details": gemini_result,
            "embedding_vector": embedding_result.get("embedding")
            if embedding_result
            else None,
            "success": gemini_result is not None and embedding_result is not None,
        }

        return final_data


class PetMatchingService:
    """
    Handles the logic for finding pet matches. This logic remains unchanged
    as it only interacts with the database.
    """

    def find_matches(
        self, query_pet_id: int, user_lat: float, user_lon: float
    ) -> list[Pet]:
        # ... (The find_matches method from your original file remains exactly the same)
        # --- OMITTED FOR BREVITY ---
        # The logic is correct and does not need to be changed.
        try:
            query_pet = Pet.objects.get(id=query_pet_id)
        except Pet.DoesNotExist:
            return []

        if query_pet.embedding is None or query_pet.breed is None:
            return []

        VISUAL_SIMILARITY_WEIGHT = 0.80
        PROXIMITY_SCORE_WEIGHT = 0.20
        user_location = Point(user_lon, user_lat, srid=4326)
        start_km, end_km = 5.0, 10.0
        c_value = 2.55
        midpoint = (start_km + end_km) / 2.0
        scale_factor = (2 * c_value) / (end_km - start_km)
        distance_meters = Distance("location", user_location)
        distance_km_float = F("distance_meters") / 1000.0
        normalized_x = (distance_km_float - midpoint) * scale_factor
        abs_normalized_x = Func(normalized_x, function="ABS")
        sigmoid_plus_c = 1.0 / (
            1.0 + Func(-10.0 * (abs_normalized_x + c_value), function="EXP")
        )
        sigmoid_minus_c = 1.0 / (
            1.0 + Func(-10.0 * (abs_normalized_x - c_value), function="EXP")
        )
        decay_score_expression = sigmoid_plus_c - sigmoid_minus_c

        proximity_score_case = Case(
            When(distance_meters__lte=start_km * 1000, then=Value(1.0)),
            When(distance_meters__gte=end_km * 1000, then=Value(0.0)),
            default=decay_score_expression,
            output_field=FloatField(),
        )

        matches = (
            Pet.objects.filter(
                breed=query_pet.breed, location__isnull=False, embedding__isnull=False
            )
            .exclude(id=query_pet.id)
            .annotate(
                distance_meters=distance_meters,
                similarity_score=1 - CosineDistance("embedding", query_pet.embedding),
                proximity_score=proximity_score_case,
            )
            .annotate(
                match_score=(
                    F("similarity_score") * VISUAL_SIMILARITY_WEIGHT
                    + F("proximity_score") * PROXIMITY_SCORE_WEIGHT
                )
            )
            .filter(distance_meters__lte=end_km * 1000)
            .order_by("-match_score")[:10]
        )

        return list(matches)
