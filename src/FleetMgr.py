"""
FleetMgr.py

Manages vehicle operations using the FleetLogisticsApiSdk, a Python SDK
generated from the Fleet Logistics API Postman collection.
"""

from __future__ import annotations

from typing import Any, Optional

from fleet_logistics_api_sdk import FleetLogisticsApiSdk


class FleetManager:
    """Wraps the FleetLogisticsApiSdk client to provide vehicle management operations."""

    def __init__(self, base_url: str, api_key: Optional[str] = None) -> None:
        """
        Initialize the FleetManager with a base URL and optional API key.

        Args:
            base_url: The base URL of the Fleet Logistics API (e.g. "https://api.example.com").
            api_key:  Optional API key used for authenticated requests.
        """
        config: dict[str, Any] = {"base_url": base_url}
        if api_key:
            config["api_key"] = api_key

        self.client = FleetLogisticsApiSdk(**config)

    # ------------------------------------------------------------------
    # Vehicle operations
    # ------------------------------------------------------------------

    def list_vehicles(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        vehicle_type: Optional[str] = None,
        organization_id: Optional[int] = None,
    ) -> Any:
        """
        Retrieve a paginated list of vehicles with optional filters.

        Args:
            skip:            Number of records to skip (default 0).
            limit:           Maximum number of records to return (default 100).
            status:          Filter by vehicle status (e.g. "active", "inactive").
            vehicle_type:    Filter by vehicle type (e.g. "truck", "van").
            organization_id: Filter by organisation ID.

        Returns:
            A list of vehicle objects returned by the API.

        Raises:
            Exception: Propagates any SDK or network error.
        """
        try:
            params: dict[str, Any] = {"skip": skip, "limit": limit}
            if status is not None:
                params["status"] = status
            if vehicle_type is not None:
                params["vehicle_type"] = vehicle_type
            if organization_id is not None:
                params["organization_id"] = organization_id

            return self.client.vehicles.list_vehicles(**params)
        except Exception as exc:
            print(f"[FleetManager] Error listing vehicles: {exc}")
            raise

    def create_vehicle(self, payload: dict[str, Any]) -> Any:
        """
        Create a new vehicle.

        Args:
            payload: Dictionary containing the vehicle fields required by the API
                     (e.g. {"name": "Truck-01", "type": "truck", ...}).

        Returns:
            The newly created vehicle object.

        Raises:
            Exception: Propagates any SDK or network error.
        """
        try:
            return self.client.vehicles.create_vehicle(body=payload)
        except Exception as exc:
            print(f"[FleetManager] Error creating vehicle: {exc}")
            raise

    def get_vehicle(self, vehicle_id: str) -> Any:
        """
        Retrieve a single vehicle by its ID.

        Args:
            vehicle_id: Unique identifier of the vehicle.

        Returns:
            The vehicle object.

        Raises:
            Exception: Propagates any SDK or network error.
        """
        try:
            return self.client.vehicles.get_vehicle(vehicle_id=vehicle_id)
        except Exception as exc:
            print(f"[FleetManager] Error fetching vehicle '{vehicle_id}': {exc}")
            raise

    def update_vehicle(self, vehicle_id: str, payload: dict[str, Any]) -> Any:
        """
        Update an existing vehicle.

        Args:
            vehicle_id: Unique identifier of the vehicle to update.
            payload:    Dictionary of fields to update.

        Returns:
            The updated vehicle object.

        Raises:
            Exception: Propagates any SDK or network error.
        """
        try:
            return self.client.vehicles.update_vehicle(
                vehicle_id=vehicle_id, body=payload
            )
        except Exception as exc:
            print(f"[FleetManager] Error updating vehicle '{vehicle_id}': {exc}")
            raise

    def delete_vehicle(self, vehicle_id: str) -> Any:
        """
        Delete a vehicle by its ID.

        Args:
            vehicle_id: Unique identifier of the vehicle to delete.

        Returns:
            The API response (typically a confirmation or empty body).

        Raises:
            Exception: Propagates any SDK or network error.
        """
        try:
            return self.client.vehicles.delete_vehicle(vehicle_id=vehicle_id)
        except Exception as exc:
            print(f"[FleetManager] Error deleting vehicle '{vehicle_id}': {exc}")
            raise

    # ------------------------------------------------------------------
    # GPS operations
    # ------------------------------------------------------------------

    def get_latest_gps(self, vehicle_id: str) -> Any:
        """
        Retrieve the latest GPS location for a vehicle.

        Args:
            vehicle_id: Unique identifier of the vehicle.

        Returns:
            The latest GPS data object for the vehicle.

        Raises:
            Exception: Propagates any SDK or network error.
        """
        try:
            return self.client.gps.get_latest_gps(vehicle_id=vehicle_id)
        except Exception as exc:
            print(
                f"[FleetManager] Error fetching GPS for vehicle '{vehicle_id}': {exc}"
            )
            raise


# ----------------------------------------------------------------------
# Demo / usage example
# ----------------------------------------------------------------------

if __name__ == "__main__":
    import json

    # ── Configuration ──────────────────────────────────────────────────
    BASE_URL = "https://api.example.com"   # Replace with your actual base URL
    API_KEY  = "your-api-key-here"         # Replace with your actual API key (or None)

    manager = FleetManager(base_url=BASE_URL, api_key=API_KEY)

    # ── 1. List vehicles ───────────────────────────────────────────────
    print("\n--- List Vehicles ---")
    vehicles = manager.list_vehicles(skip=0, limit=10, status="active")
    print(json.dumps(vehicles, indent=2, default=str))

    # ── 2. Create a vehicle ────────────────────────────────────────────
    print("\n--- Create Vehicle ---")
    new_vehicle_payload: dict[str, Any] = {
        "name": "Demo Truck 01",
        "type": "truck",
        "status": "active",
        "organization_id": 1432,
        "license_plate": "DEMO-001",
    }
    created_vehicle = manager.create_vehicle(payload=new_vehicle_payload)
    print(json.dumps(created_vehicle, indent=2, default=str))

    # Extract the ID of the newly created vehicle for subsequent calls
    vehicle_id: str = str(created_vehicle.get("id") or created_vehicle.get("vehicle_id"))
    print(f"\nCreated vehicle ID: {vehicle_id}")

    # ── 3. Get vehicle by ID ───────────────────────────────────────────
    print("\n--- Get Vehicle ---")
    fetched_vehicle = manager.get_vehicle(vehicle_id=vehicle_id)
    print(json.dumps(fetched_vehicle, indent=2, default=str))

    # ── 4. Update the vehicle ──────────────────────────────────────────
    print("\n--- Update Vehicle ---")
    update_payload: dict[str, Any] = {
        "name": "Demo Truck 01 (Updated)",
        "status": "maintenance",
    }
    updated_vehicle = manager.update_vehicle(
        vehicle_id=vehicle_id, payload=update_payload
    )
    print(json.dumps(updated_vehicle, indent=2, default=str))

    # ── 5. Get latest GPS location ─────────────────────────────────────
    print("\n--- Get Latest GPS ---")
    gps_data = manager.get_latest_gps(vehicle_id=vehicle_id)
    print(json.dumps(gps_data, indent=2, default=str))

    # ── 6. Delete the vehicle ──────────────────────────────────────────
    print("\n--- Delete Vehicle ---")
    delete_response = manager.delete_vehicle(vehicle_id=vehicle_id)
    print(json.dumps(delete_response, indent=2, default=str))

    print("\nDemo complete.")
