from typing import Tuple, List, Dict, Any, Optional
import random

from .unit import Unit
from .squad import Squad, FormationType
from .dimensioneer import Dimensioneer
from .portal_archer import PortalArcher
from .tech_grenadier import TechGrenadier
from .gromflomite import Gromflomite

class UnitFactory:
    """
    Factory class for creating units and squads.
    Centralizes unit creation logic and provides utility methods for squad composition.
    """
    
    @staticmethod
    def create_unit(unit_type: str, position: Tuple[float, float, float], faction: str = "player") -> Optional[Unit]:
        """
        Create a unit of the specified type
        
        Args:
            unit_type: Type of unit to create
            position: Position to place the unit
            faction: Faction the unit belongs to
            
        Returns:
            Unit instance or None if type is invalid
        """
        if unit_type == "dimensioneer":
            return Dimensioneer(position, faction)
        elif unit_type == "portal_archer":
            return PortalArcher(position, faction)
        elif unit_type == "tech_grenadier":
            return TechGrenadier(position, faction)
        elif unit_type == "gromflomite":
            return Gromflomite(position, faction)
        else:
            return None
    
    @staticmethod
    def create_squad(squad_type: str, position: Tuple[float, float], 
                    unit_count: int = 5, faction: str = "player", 
                    name: str = None) -> Squad:
        """
        Create a squad of units of a specific type
        
        Args:
            squad_type: Type of units in the squad
            position: Center position for the squad
            unit_count: Number of units to create
            faction: Faction the squad belongs to
            name: Optional name for the squad (auto-generated if None)
            
        Returns:
            Squad instance with units added
        """
        # Generate squad name if not provided
        if name is None:
            prefix = "Player" if faction == "player" else "Enemy"
            name = f"{prefix} {squad_type.capitalize()} Squad {random.randint(1, 999)}"
        
        # Create squad
        squad = Squad(name, faction, position)
        
        # Set appropriate formation based on unit type
        if squad_type == "dimensioneer":
            squad.set_formation(FormationType.LINE)
        elif squad_type == "portal_archer":
            squad.set_formation(FormationType.WEDGE)
        elif squad_type == "tech_grenadier":
            squad.set_formation(FormationType.SCATTERED)
        elif squad_type == "gromflomite":
            squad.set_formation(FormationType.LINE)
        
        # Add units to the squad
        for i in range(unit_count):
            # Create a unit at a slight offset from the center
            offset_x = random.uniform(-5, 5)
            offset_y = random.uniform(-5, 5)
            unit_position = (position[0] + offset_x, position[1] + offset_y, 0)
            
            # Create and add the unit
            unit = UnitFactory.create_unit(squad_type, unit_position, faction)
            if unit:
                squad.add_unit(unit)
        
        # Position units in formation
        squad._update_formation()
        
        return squad
    
    @staticmethod
    def create_mixed_squad(position: Tuple[float, float], 
                         composition: Dict[str, int], 
                         faction: str = "player",
                         name: str = None) -> Squad:
        """
        Create a squad with a mix of unit types
        
        Args:
            position: Center position for the squad
            composition: Dict mapping unit types to counts (e.g. {"dimensioneer": 3, "portal_archer": 2})
            faction: Faction the squad belongs to
            name: Optional name for the squad
            
        Returns:
            Squad instance with mixed units added
        """
        # Generate squad name if not provided
        if name is None:
            prefix = "Player" if faction == "player" else "Enemy"
            name = f"{prefix} Mixed Squad {random.randint(1, 999)}"
        
        # Create squad
        squad = Squad(name, faction, position)
        
        # Add units of each type
        for unit_type, count in composition.items():
            for i in range(count):
                # Create a unit at a slight offset from the center
                offset_x = random.uniform(-5, 5)
                offset_y = random.uniform(-5, 5)
                unit_position = (position[0] + offset_x, position[1] + offset_y, 0)
                
                # Create and add the unit
                unit = UnitFactory.create_unit(unit_type, unit_position, faction)
                if unit:
                    squad.add_unit(unit)
        
        # Position units in formation
        squad._update_formation()
        
        return squad
    
    @staticmethod
    def create_player_starter_squad(position: Tuple[float, float]) -> Squad:
        """
        Create a balanced starter squad for the player
        
        Args:
            position: Position for the squad
            
        Returns:
            A balanced squad with mixed unit types
        """
        return UnitFactory.create_mixed_squad(
            position,
            {
                "dimensioneer": 3,
                "portal_archer": 2,
                "tech_grenadier": 1
            },
            "player",
            "Rick's Task Force Alpha"
        )
    
    @staticmethod
    def create_enemy_patrol_squad(position: Tuple[float, float]) -> Squad:
        """
        Create a basic enemy patrol squad
        
        Args:
            position: Position for the squad
            
        Returns:
            An enemy squad with Gromflomites
        """
        return UnitFactory.create_squad(
            "gromflomite",
            position,
            4,
            "enemy",
            "Federation Patrol"
        )
