"""Thin wrapper around the official Neo4j driver."""

import time
from typing import Any, Self

from neo4j import GraphDatabase, RoutingControl
from neo4j.exceptions import AuthError, ConnectionAcquisitionTimeoutError, ServiceUnavailable, SessionExpired

from continuity_editor.config import Neo4jSettings, get_neo4j_settings

IDLE_REFRESH_SECONDS = 120
_ATTEMPTS = 4

# Summary counters reported by write(); zero-valued ones are left out.
_COUNTERS = (
    "nodes_created",
    "nodes_deleted",
    "relationships_created",
    "relationships_deleted",
    "properties_set",
    "labels_added",
    "indexes_added",
    "constraints_added",
)


class Neo4jConnection:
    """One driver (connection pool) shared by the whole pipeline.

    Usage:
        with Neo4jConnection() as conn:
            conn.verify()
            rows = conn.query("MATCH (c:Character) RETURN c.name AS name")
    """

    def __init__(self, settings: Neo4jSettings | None = None) -> None:
        self.settings = settings or get_neo4j_settings()
        self.database = self.settings.neo4j_database
        self._driver = self._new_driver()
        self._last_used = time.monotonic()

    def _new_driver(self):
        return GraphDatabase.driver(
            self.settings.neo4j_uri,
            auth=(self.settings.neo4j_username, self.settings.neo4j_password.get_secret_value()),
            liveness_check_timeout=30,
            max_connection_lifetime=600,
        )

    def _fresh_driver(self) -> None:
        """Replace the driver, and with it every pooled connection."""
        try:
            self._driver.close()
        except Exception:  # an already-broken pool may fail to close; it is discarded either way
            pass
        self._driver = self._new_driver()

    def verify(self) -> dict[str, str]:
        """Check the server is reachable and the credentials work, and return server details."""
        try:
            info = self._driver.get_server_info()
        except AuthError as exc:
            raise RuntimeError(
                "Neo4j rejected the credentials: check NEO4J_USERNAME and NEO4J_PASSWORD in .env."
            ) from exc
        except ServiceUnavailable as exc:
            raise RuntimeError(
                f"Could not reach Neo4j at {self.settings.neo4j_uri}. AuraDB Free pauses after a few "
                "days without use: resume the instance at https://console.neo4j.io, then check NEO4J_URI."
            ) from exc
        return {
            "address": str(info.address),
            "agent": info.agent,
            "protocol": ".".join(map(str, info.protocol_version)),
        }

    def query(self, cypher: str, **params: Any) -> list[dict[str, Any]]:
        """Run a read query and return the rows as plain dicts."""
        records, _, _ = self._execute(cypher, params, routing_=RoutingControl.READ)
        return [record.data() for record in records]

    def write(self, cypher: str, **params: Any) -> dict[str, int]:
        """Run a write query and return what it changed, e.g. {"nodes_created": 2}."""
        _, summary, _ = self._execute(cypher, params)
        counters = summary.counters
        return {name: getattr(counters, name) for name in _COUNTERS if getattr(counters, name)}

    def _execute(self, cypher: str, params: dict[str, Any], **options: Any):
        """execute_query, robust to connections that the network has silently cut.

        Between your computer and AuraDB, a connection left idle for a few minutes (while the
        LLM works) can be dropped without either end being told; even testing such a connection
        can hang. So connections idle for over IDLE_REFRESH_SECONDS are never reused, and a
        network failure is retried on brand-new connections instead of ending a long run.
        """
        if time.monotonic() - self._last_used > IDLE_REFRESH_SECONDS:
            self._fresh_driver()
        for attempt in range(_ATTEMPTS):
            try:
                result = self._driver.execute_query(cypher, params, database_=self.database, **options)
                self._last_used = time.monotonic()
                return result
            except (SessionExpired, ServiceUnavailable, ConnectionAcquisitionTimeoutError):
                if attempt == _ATTEMPTS - 1:
                    raise
                time.sleep(5 * (attempt + 1))
                self._fresh_driver()

    def close(self) -> None:
        self._driver.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
