"""
CareVault - Consent & Access Agent

This agent manages consent-based access to family health records.

Responsibilities:
- Create access requests
- Grant access
- Check whether access is allowed
- Control what type of records can be accessed
- Revoke access
- Keep access decisions explicit

Important:
No family member can access another person's health records
unless the record owner has granted permission.
"""


class ConsentAccessAgent:

    def __init__(self):
        self.name = "Consent & Access Agent"

        # Stores consent information in memory for now.
        # Later this will be replaced with a database.
        self.consents = {}

        # Available permission scopes
        self.permission_scopes = {
            "all_records",
            "lab_reports",
            "prescriptions",
            "medications",
            "doctor_summaries",
            "health_trends"
        }

    # ---------------------------------------------------------
    # CREATE ACCESS REQUEST
    # ---------------------------------------------------------

    def request_access(
        self,
        requester_id,
        owner_id,
        scope,
        reason=None
    ):
        """
        Request access to another family member's health records.

        requester_id = person requesting access
        owner_id     = person who owns the health records
        scope        = type of records requested
        """

        if not requester_id or not owner_id:
            return {
                "success": False,
                "message": "Requester ID and owner ID are required."
            }

        if requester_id == owner_id:
            return {
                "success": True,
                "status": "not_required",
                "message": "Users can access their own records."
            }

        if scope not in self.permission_scopes:
            return {
                "success": False,
                "message": f"Invalid permission scope: {scope}"
            }

        request_id = (
            f"{requester_id}_{owner_id}_{scope}"
        )

        self.consents[request_id] = {
            "request_id": request_id,
            "requester_id": requester_id,
            "owner_id": owner_id,
            "scope": scope,
            "reason": reason,
            "status": "pending"
        }

        return {
            "success": True,
            "request_id": request_id,
            "requester_id": requester_id,
            "owner_id": owner_id,
            "scope": scope,
            "status": "pending",
            "message": "Consent request created."
        }

    # ---------------------------------------------------------
    # GRANT ACCESS
    # ---------------------------------------------------------

    def grant_access(
        self,
        request_id,
        owner_id
    ):
        """
        Grant access to a pending request.

        Only the health-record owner can grant consent.
        """

        consent = self.consents.get(request_id)

        if not consent:
            return {
                "success": False,
                "message": "Consent request not found."
            }

        if consent["owner_id"] != owner_id:
            return {
                "success": False,
                "message": (
                    "Only the record owner can grant access."
                )
            }

        if consent["status"] != "pending":
            return {
                "success": False,
                "message": (
                    f"Request is already {consent['status']}."
                )
            }

        consent["status"] = "granted"

        return {
            "success": True,
            "request_id": request_id,
            "status": "granted",
            "message": "Access granted successfully."
        }

    # ---------------------------------------------------------
    # DENY ACCESS
    # ---------------------------------------------------------

    def deny_access(
        self,
        request_id,
        owner_id
    ):
        """
        Deny a pending access request.
        """

        consent = self.consents.get(request_id)

        if not consent:
            return {
                "success": False,
                "message": "Consent request not found."
            }

        if consent["owner_id"] != owner_id:
            return {
                "success": False,
                "message": (
                    "Only the record owner can deny access."
                )
            }

        if consent["status"] != "pending":
            return {
                "success": False,
                "message": (
                    f"Request is already {consent['status']}."
                )
            }

        consent["status"] = "denied"

        return {
            "success": True,
            "request_id": request_id,
            "status": "denied",
            "message": "Access request denied."
        }

    # ---------------------------------------------------------
    # REVOKE ACCESS
    # ---------------------------------------------------------

    def revoke_access(
        self,
        request_id,
        owner_id
    ):
        """
        Revoke previously granted access.

        The owner can revoke access at any time.
        """

        consent = self.consents.get(request_id)

        if not consent:
            return {
                "success": False,
                "message": "Consent record not found."
            }

        if consent["owner_id"] != owner_id:
            return {
                "success": False,
                "message": (
                    "Only the record owner can revoke access."
                )
            }

        if consent["status"] != "granted":
            return {
                "success": False,
                "message": "Access is not currently granted."
            }

        consent["status"] = "revoked"

        return {
            "success": True,
            "request_id": request_id,
            "status": "revoked",
            "message": "Access has been revoked."
        }

    # ---------------------------------------------------------
    # CHECK ACCESS
    # ---------------------------------------------------------

    def check_access(
        self,
        requester_id,
        owner_id,
        scope
    ):
        """
        Check whether a requester currently has permission
        to access a specific type of health record.
        """

        # Users always have access to their own records.
        if requester_id == owner_id:
            return {
                "allowed": True,
                "reason": "Owner accessing own records."
            }

        # Check all consent records.
        for consent in self.consents.values():

            if (
                consent["requester_id"] == requester_id
                and consent["owner_id"] == owner_id
                and consent["status"] == "granted"
            ):

                granted_scope = consent["scope"]

                if (
                    granted_scope == "all_records"
                    or granted_scope == scope
                ):
                    return {
                        "allowed": True,
                        "reason": "Valid consent found.",
                        "scope": granted_scope
                    }

        return {
            "allowed": False,
            "reason": "No valid consent found."
        }

    # ---------------------------------------------------------
    # GET USER ACCESS
    # ---------------------------------------------------------

    def get_access_for_user(self, user_id):
        """
        Return all consent records involving a user.
        """

        records = []

        for consent in self.consents.values():

            if (
                consent["requester_id"] == user_id
                or consent["owner_id"] == user_id
            ):
                records.append(consent.copy())

        return {
            "success": True,
            "user_id": user_id,
            "consents": records
        }

    # ---------------------------------------------------------
    # GET REQUEST
    # ---------------------------------------------------------

    def get_request(self, request_id):
        """
        Retrieve a specific consent request.
        """

        consent = self.consents.get(request_id)

        if not consent:
            return {
                "success": False,
                "message": "Consent request not found."
            }

        return {
            "success": True,
            "consent": consent.copy()
        }