"""Auto-detect battery/inverter entities for dual battery setup.

Supports any inverter brand (SolaX, Growatt, Sungrow, Goodwe, etc.)
by grouping entities through the device registry and matching generic
battery-related keywords.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

# Keywords used to identify battery-related entities
_SOC_KEYWORDS = ["battery_capacity", "battery_soc", "soc", "state_of_charge", "state of charge", "battery_level"]
_POWER_KEYWORDS = ["battery_power", "battery_power_charge"]
_CURRENT_LIMIT_KEYWORDS = ["battery_charge_max_current", "charge_max_current", "current_limit", "charge_current_limit", "max_charge_current"]
_HOUSE_LOAD_KEYWORDS = ["house_load", "home_consumption", "house_power", "consumption", "home_load", "grid_consumption"]


def _keyword_match(name: str, keywords: list[str]) -> bool:
    name = name.lower().replace("_", " ").replace("-", " ")
    return any(kw.replace("_", " ") in name for kw in keywords)


def _score_device(entities: list[dict]) -> int:
    """Score a device group for battery/inverter relevance (higher = better)."""
    score = 0
    has_soc = has_power = has_current = False
    for e in entities:
        name = e.get("name", "")
        dc = e.get("device_class", "")
        if _keyword_match(name, _SOC_KEYWORDS) or dc == "battery":
            has_soc = True
            score += 20
        if _keyword_match(name, _POWER_KEYWORDS) or dc == "power":
            has_power = True
            score += 10
        if _keyword_match(name, _CURRENT_LIMIT_KEYWORDS) or dc == "current":
            has_current = True
            score += 10
        if _keyword_match(name, _HOUSE_LOAD_KEYWORDS):
            score += 10
        if "battery" in name.split():
            score += 5
        if "inverter" in name.split():
            score += 3
    if has_soc and has_power:
        score += 15
    if has_soc and has_current:
        score += 10
    return score


def _pick(entities: list[dict], keywords: list[str], preferred_domain: str | None = None, device_class: str | None = None) -> str | None:
    """Pick the best matching entity for a role from a device group."""
    scored: list[tuple[int, str]] = []
    for e in entities:
        ent = e["entity_id"]
        name = e.get("name", "")
        dc = e.get("device_class", "")
        score = 0
        if _keyword_match(name, keywords):
            score += 30
        if preferred_domain and ent.startswith(f"{preferred_domain}."):
            score += 20
        if device_class and dc == device_class:
            score += 15
        if score > 0:
            scored.append((score, ent))
    scored.sort(reverse=True)
    return scored[0][1] if scored else None


async def async_detect_entities(hass: HomeAssistant) -> dict:
    """Scan entities and return detected Battery A and B mapping.

    Returns: {"a": {"soc": eid, "power": eid, "current_limit": eid, "house_load": eid},
               "b": {...}}
    """
    states = hass.states.async_all()

    # Build device → entities mapping from entity registry
    try:
        from homeassistant.helpers.entity_registry import async_get as get_er
        er = get_er(hass)
    except Exception:
        er = None

    by_device: dict[str | None, list[dict]] = {}
    by_prefix: dict[str, list[dict]] = {}

    for state in states:
        info = {
            "entity_id": state.entity_id,
            "name": (state.attributes.get("friendly_name") or state.entity_id.split(".")[-1]).lower().replace("_", " "),
            "device_class": state.attributes.get("device_class"),
        }
        device_id = None
        if er:
            entry = er.async_get(state.entity_id)
            if entry:
                device_id = entry.device_id
        by_device.setdefault(device_id, []).append(info)

        # Also group by prefix for strategy 2
        _group_by_prefix(info, by_prefix)

    # Strategy 1: Score device groups, pick top 2
    device_scores: list[tuple[int, str | None]] = []
    for dev_id, ents in by_device.items():
        score = _score_device(ents)
        if score > 0:
            device_scores.append((score, dev_id))
    device_scores.sort(reverse=True)

    if len(device_scores) >= 2:
        top_devices = [device_scores[0][1], device_scores[1][1]]
        mapping = {}
        for key, dev_id in zip(("a", "b"), top_devices):
            ents = by_device[dev_id]
            mapping[key] = _map_device_entities(ents)
        if mapping.get("a", {}).get("soc"):
            return mapping

    # Strategy 2: Prefix-based grouping (SolaX, or numeric suffixes)
    if by_prefix:
        sorted_prefixes = sorted(by_prefix.keys())
        if len(sorted_prefixes) >= 2:
            mapping = {}
            for key, prefix in zip(("a", "b"), sorted_prefixes[:2]):
                ents = by_prefix[prefix]
                mapping[key] = _map_device_entities(ents)
            if mapping.get("a", {}).get("soc"):
                return mapping

    # Strategy 3: Fallback — scan all entities without device grouping
    all_ents = []
    for state in states:
        all_ents.append({
            "entity_id": state.entity_id,
            "name": (state.attributes.get("friendly_name") or state.entity_id.split(".")[-1]).lower().replace("_", " "),
            "device_class": state.attributes.get("device_class"),
        })
    soc = _pick(all_ents, _SOC_KEYWORDS, device_class="battery")
    power = _pick(all_ents, _POWER_KEYWORDS, device_class="power")
    current = _pick(all_ents, _CURRENT_LIMIT_KEYWORDS, preferred_domain="number")
    house = _pick(all_ents, _HOUSE_LOAD_KEYWORDS, device_class="power")
    result = {}
    if soc or power or current or house:
        result["a"] = {"soc": soc, "power": power, "current_limit": current, "house_load": house}
    return result


def _group_by_prefix(info: dict, groups: dict[str, list[dict]]) -> None:
    """Try to group entity by an inverter/battery prefix in its ID."""
    eid = info["entity_id"].split(".")[-1]
    import re
    for match in re.finditer(r"(tock_solax[12]|solax[12]|inverter[12]|battery[12]|pvo[12]|bat[ab12])", eid):
        groups.setdefault(match.group(0), []).append(info)
        return
    for match in re.finditer(r"^(\w+?)[_\.]?(?:battery|inverter|soc|power)", eid, re.IGNORECASE):
        groups.setdefault(match.group(1), []).append(info)
        return


def _map_device_entities(entities: list[dict]) -> dict:
    """Map entities from a device group to SOC/Power/CurrentLimit/HouseLoad."""
    soc = _pick(entities, _SOC_KEYWORDS, device_class="battery")
    power = _pick(entities, _POWER_KEYWORDS, device_class="power")
    current_limit = _pick(entities, _CURRENT_LIMIT_KEYWORDS, preferred_domain="number")
    house_load = _pick(entities, _HOUSE_LOAD_KEYWORDS, device_class="power")
    return {
        "soc": soc,
        "power": power,
        "current_limit": current_limit,
        "house_load": house_load,
    }


async def async_build_defaults(hass: HomeAssistant) -> dict:
    """Build defaults dict for the config flow, keyed by CONF_ constants."""
    detected = await async_detect_entities(hass)
    from .const import (
        CONF_BATTERY_A_CURRENT_LIMIT,
        CONF_BATTERY_A_HOUSE_LOAD,
        CONF_BATTERY_A_NAME,
        CONF_BATTERY_A_POWER,
        CONF_BATTERY_A_SOC,
        CONF_BATTERY_B_CURRENT_LIMIT,
        CONF_BATTERY_B_HOUSE_LOAD,
        CONF_BATTERY_B_NAME,
        CONF_BATTERY_B_POWER,
        CONF_BATTERY_B_SOC,
    )
    defaults = {}
    if "a" in detected:
        defaults[CONF_BATTERY_A_NAME] = "Battery A"
        defaults[CONF_BATTERY_A_SOC] = detected["a"].get("soc") or ""
        defaults[CONF_BATTERY_A_POWER] = detected["a"].get("power") or ""
        defaults[CONF_BATTERY_A_CURRENT_LIMIT] = detected["a"].get("current_limit") or ""
        defaults[CONF_BATTERY_A_HOUSE_LOAD] = detected["a"].get("house_load") or ""
    if "b" in detected:
        defaults[CONF_BATTERY_B_NAME] = "Battery B"
        defaults[CONF_BATTERY_B_SOC] = detected["b"].get("soc") or ""
        defaults[CONF_BATTERY_B_POWER] = detected["b"].get("power") or ""
        defaults[CONF_BATTERY_B_CURRENT_LIMIT] = detected["b"].get("current_limit") or ""
        defaults[CONF_BATTERY_B_HOUSE_LOAD] = detected["b"].get("house_load") or ""
    return defaults
