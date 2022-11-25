#!/usr/bin/env python3
# Copyright 2022 Johan Hallbäck
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charm the service.

Refer to the following post for a quick-start guide that will help you
develop a new k8s charm using the Operator Framework:

    https://discourse.charmhub.io/t/4208
"""

import logging
import time

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus, WaitingStatus, MaintenanceStatus
from ops.framework import StoredState

from samba_ctdb_cluster_ops_manager import SambaCTDBManager

# Log messages can be retrieved using juju debug-log
logger = logging.getLogger(__name__)

VALID_LOG_LEVELS = ["info", "debug", "warning", "error", "critical"]


class SambaCTDBClusterCharm(CharmBase):
    """Charm the service."""

    # https://juju.is/docs/sdk/constructs#heading--stored-state
    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.samba_ctdb_manager = SambaCTDBManager()
        self.framework.observe(self.on.install, self._on_install)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.update_status, self._on_update_status)

        # Peer relation stuff - https://juju.is/docs/sdk/integration
        # Implement these!
        self.framework.observe(self.on.leader_elected, self._on_leader_elected)
        self.framework.observe(self.on.replicas_relation_joined, self._on_replicas_relation_joined)
        self.framework.observe(self.on.replicas_relation_departed, self._on_replicas_relation_departed)
        self.framework.observe(self.on.replicas_relation_changed, self._on_replicas_relation_changed)

        self._stored.set_default(leader_ip="")

    def _on_install(self, event):
        self.unit.status = MaintenanceStatus("Charm is now being installed")
        logger.info("Our charm is now being installed")
        self.samba_ctdb_manager.install_ctdb()
        self.unit.status = ActiveStatus("Charm is now installed")

    def _on_config_changed(self, event):
        """Handle changed configuration.

        Change this example to suit your needs. If you don't need to handle config, you can remove
        this method.

        Learn more about config at https://juju.is/docs/sdk/config
        """
        # Fetch the new config value
        log_level = self.model.config["log-level"].lower()

        # Do some validation of the configuration option
        if log_level in VALID_LOG_LEVELS:
            self.unit.status = MaintenanceStatus("Charm is now being configured")
            logger.info("Heyhey configured log level %s" % log_level)
        else:
            # In this case, the config option is bad, so block the charm and notify the operator.
            self.unit.status = BlockedStatus("invalid log level: '{log_level}'")

    def _on_start(self, event):
        self.unit.status = ActiveStatus("Charm is now started")
        logger.info("Our charm is now started")

    def _on_update_status(self, event):
        now = time.ctime()
        self.unit.status = ActiveStatus("Charm was updated at %s" % now)
        logger.info("Our charm was updated at %s" % now)

    def _on_leader_elected(self, event: LeaderElectedEvent) -> None:
        """Handle the leader-elected event"""
        logging.debug("Leader %s setting some data!", self.unit.name)
        # Get the peer relation object
        peer_relation = self.model.get_relation("replicas")
        # Get the bind address from the juju model
        # Convert to string as relation data must always be a string
        ip = str(self.model.get_binding(peer_relation).network.bind_address)
        # Update some data to trigger a replicas_relation_changed event
        peer_relation.data[self.app].update({"leader-ip": ip})

    def _on_replicas_relation_joined(self, event: RelationJoinedEvent) -> None:
        logger.info("Leader elected event")
        """Handle relation-joined event for the replicas relation"""
        logger.debug("Hello from %s to %s", self.unit.name, event.unit.name)

        # Check if we're the leader
        if self.unit.is_leader():
            # Get the bind address from the juju model
            ip = str(self.model.get_binding(event.relation).network.bind_address)
            logging.debug("Leader %s setting some data!", self.unit.name)
            event.relation.data[self.app].update({"leader-ip": ip})

        # Update our unit data bucket in the relation
        event.relation.data[self.unit].update({"unit-data": self.unit.name})

    def _on_replicas_relation_departed(self, event: RelationDepartedEvent) -> None:
        logger.info("Leader departed event")
        """Handle relation-departed event for the replicas relation"""
        logger.debug("Goodbye from %s to %s", self.unit.name, event.unit.name)

    def _on_replicas_relation_changed(self, event: RelationChangedEvent) -> None:
        logger.info("Leader changed event")
        """Handle relation-changed event for the replicas relation"""
        logging.debug("Unit %s can see the following data: %s", self.unit.name, event.relation.data.keys())
        # Fetch an item from the application data bucket
        leader_ip_value = event.relation.data[self.app].get("leader-ip")
        # Store the latest copy locally in our state store
        if leader_ip_value and leader_ip_value != self._stored.leader_ip:
            self._stored.leader_ip = leader_ip_value


if __name__ == "__main__":  # pragma: nocover
    main(SambaCTDBClusterCharm)