import os
import json
from typing import Dict, List, Optional
from game.mission.mission import Mission

class MissionManager:
    """
    Manages loading, tracking, and progressing through game missions.
    """
    
    def __init__(self, missions_dir: str = None):
        """
        Initialize the mission manager
        
        Args:
            missions_dir: Directory containing mission JSON files
        """
        self.missions_dir = missions_dir or os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'missions')
        self.missions = {}  # mission_id -> Mission
        self.current_mission = None
        self.completed_missions = []
        
        # Create missions directory if it doesn't exist
        os.makedirs(self.missions_dir, exist_ok=True)
    
    def load_all_missions(self) -> bool:
        """
        Load all missions from the missions directory
        
        Returns:
            True if missions were loaded, False otherwise
        """
        try:
            # Reset missions dict
            self.missions = {}
            
            # Check if directory exists
            if not os.path.exists(self.missions_dir):
                print(f"Missions directory not found: {self.missions_dir}")
                return False
                
            # Find all JSON files in the directory
            mission_files = [f for f in os.listdir(self.missions_dir) if f.endswith('.json')]
            
            if not mission_files:
                print(f"No mission files found in: {self.missions_dir}")
                return False
                
            # Load each mission file
            for filename in mission_files:
                filepath = os.path.join(self.missions_dir, filename)
                mission = Mission("", "", "")  # Create empty mission
                if mission.load_from_file(filepath):
                    self.missions[mission.mission_id] = mission
            
            print(f"Loaded {len(self.missions)} missions")
            return True
        except Exception as e:
            print(f"Error loading missions: {e}")
            return False
    
    def create_default_missions(self) -> None:
        """
        Create default missions if none exist in the missions directory
        """
        # Create default mission data
        missions = [
            {
                "mission_id": "citadel_crisis",
                "name": "Citadel Crisis",
                "description": "Federation forces have launched an assault on the Citadel. Defeat the waves of Gromflomites and protect the citizens!",
                "map_name": "citadel",
                "difficulty": "normal",
                "time_limit": 0,
                "objectives": [
                    {
                        "id": "defeat_enemies",
                        "type": "defeat_all",
                        "description": "Defeat all enemy forces",
                        "mandatory": True
                    },
                    {
                        "id": "protect_civilians",
                        "type": "survive_time",
                        "description": "Protect civilians for 5 minutes",
                        "time": 300,
                        "mandatory": True
                    }
                ],
                "player_squads": [
                    {
                        "type": "balanced",
                        "position": [0, 0, 0],
                        "size": 8,
                        "name": "Defense Squad Alpha"
                    },
                    {
                        "type": "archer",
                        "position": [-50, 50, 0],
                        "size": 5,
                        "name": "Defense Squad Bravo"
                    }
                ],
                "enemy_waves": [
                    {
                        "trigger": "time",
                        "trigger_time": 10,
                        "squads": [
                            {
                                "type": "gromflomite",
                                "position": [200, 200, 0],
                                "size": 10,
                                "name": "First Wave"
                            }
                        ]
                    },
                    {
                        "trigger": "enemies_defeated",
                        "squads": [
                            {
                                "type": "gromflomite",
                                "position": [200, -200, 0],
                                "size": 15,
                                "name": "Second Wave"
                            },
                            {
                                "type": "gromflomite",
                                "position": [-200, 200, 0],
                                "size": 5,
                                "name": "Flanking Force"
                            }
                        ]
                    },
                    {
                        "trigger": "enemies_defeated",
                        "squads": [
                            {
                                "type": "gromflomite",
                                "position": [250, 0, 0],
                                "size": 20,
                                "name": "Final Wave"
                            }
                        ]
                    }
                ]
            },
            {
                "mission_id": "purge_planet",
                "name": "Purge Planet Patrol",
                "description": "It's the annual Purge on this planet! Rescue stranded scientists while defending against hostile purgers.",
                "map_name": "purge_planet",
                "difficulty": "hard",
                "time_limit": 600,  # 10 minutes
                "objectives": [
                    {
                        "id": "reach_extraction",
                        "type": "reach_position",
                        "description": "Reach the extraction point",
                        "position": [300, 300, 0],
                        "radius": 20,
                        "mandatory": True
                    },
                    {
                        "id": "defeat_all",
                        "type": "defeat_all",
                        "description": "Defeat all purgers (optional)",
                        "mandatory": False
                    }
                ],
                "player_squads": [
                    {
                        "type": "balanced",
                        "position": [0, 0, 0],
                        "size": 6,
                        "name": "Rescue Team"
                    },
                    {
                        "type": "grenadier",
                        "position": [20, -20, 0],
                        "size": 4,
                        "name": "Heavy Support"
                    }
                ],
                "enemy_waves": [
                    {
                        "trigger": "time",
                        "trigger_time": 0,
                        "squads": [
                            {
                                "type": "gromflomite",
                                "position": [100, 100, 0],
                                "size": 8,
                                "name": "Purgers Alpha"
                            }
                        ]
                    },
                    {
                        "trigger": "time",
                        "trigger_time": 120,
                        "squads": [
                            {
                                "type": "gromflomite",
                                "position": [-100, 150, 0],
                                "size": 10,
                                "name": "Purgers Beta"
                            }
                        ]
                    },
                    {
                        "trigger": "time",
                        "trigger_time": 240,
                        "squads": [
                            {
                                "type": "gromflomite",
                                "position": [150, -100, 0],
                                "size": 12,
                                "name": "Purgers Gamma"
                            }
                        ]
                    },
                    {
                        "trigger": "time",
                        "trigger_time": 360,
                        "squads": [
                            {
                                "type": "gromflomite",
                                "position": [200, 200, 0],
                                "size": 15,
                                "name": "Purgers Delta"
                            }
                        ]
                    }
                ]
            }
        ]
        
        # Create "Cronenberg Infestation" mission
        cronenberg_mission = {
            "mission_id": "cronenberg_infestation",
            "name": "Cronenberg Infestation",
            "description": "A Cronenberg outbreak has occurred on Planet C-137. Eliminate all infected creatures and secure the area.",
            "map_name": "c137_outpost",
            "difficulty": "hard",
            "time_limit": 600,  # 10 minutes
            "objectives": [
                {
                    "id": "clear_zone_a",
                    "type": "defeat_all",
                    "description": "Clear Cronenbergs from Zone A",
                    "target_group": "zone_a_enemies",
                    "mandatory": True
                },
                {
                    "id": "reach_laboratory",
                    "type": "reach_position",
                    "description": "Reach the containment laboratory",
                    "position": [200, 200, 0],
                    "radius": 30,
                    "mandatory": True
                },
                {
                    "id": "protect_scientists",
                    "type": "survive_time",
                    "description": "Protect scientists for 5 minutes",
                    "time": 300,
                    "mandatory": True
                }
            ],
            "player_squads": [
                {
                    "type": "balanced",
                    "position": [0, 0, 0],
                    "size": 8,
                    "name": "Containment Squad Alpha"
                },
                {
                    "type": "archer",
                    "position": [-30, 30, 0],
                    "size": 5,
                    "name": "Support Team"
                }
            ],
            "enemy_waves": [
                {
                    "trigger": "time",
                    "trigger_time": 5,
                    "squads": [
                        {
                            "type": "cronenberg",
                            "position": [150, 150, 0],
                            "size": 10,
                            "name": "Cronenberg Pack Alpha",
                            "group": "zone_a_enemies"
                        }
                    ]
                },
                {
                    "trigger": "objective_complete",
                    "trigger_objective": "clear_zone_a",
                    "squads": [
                        {
                            "type": "cronenberg",
                            "position": [250, -150, 0],
                            "size": 15,
                            "name": "Cronenberg Pack Beta"
                        },
                        {
                            "type": "cronenberg",
                            "position": [-200, 200, 0],
                            "size": 5,
                            "name": "Cronenberg Scouts"
                        }
                    ]
                },
                {
                    "trigger": "time",
                    "trigger_time": 300,  # 5 minutes in
                    "squads": [
                        {
                            "type": "cronenberg_alpha",
                            "position": [0, 250, 0],
                            "size": 1,
                            "name": "Cronenberg Alpha Specimen"
                        }
                    ]
                }
            ]
        }
        
        # Create "Showdown at Blood Ridge" mission
        blood_ridge_mission = {
            "mission_id": "blood_ridge_showdown",
            "name": "Showdown at Blood Ridge",
            "description": "The Federation forces are making their last stand at Blood Ridge. Defeat them before reinforcements arrive.",
            "map_name": "blood_ridge",
            "difficulty": "extreme",
            "time_limit": 900,  # 15 minutes
            "objectives": [
                {
                    "id": "eliminate_command",
                    "type": "defeat_all",
                    "description": "Eliminate Federation Command Post",
                    "target_group": "command_post",
                    "mandatory": True
                },
                {
                    "id": "destroy_turrets",
                    "type": "defeat_all",
                    "description": "Destroy all defensive turrets",
                    "target_group": "turrets",
                    "mandatory": True
                },
                {
                    "id": "hold_ridge",
                    "type": "survive_time",
                    "description": "Hold Blood Ridge for 10 minutes",
                    "time": 600,
                    "mandatory": True
                },
                {
                    "id": "rescue_prisoners",
                    "type": "reach_position",
                    "description": "Rescue prisoners (optional)",
                    "position": [-150, -150, 0],
                    "radius": 20,
                    "mandatory": False
                }
            ],
            "player_squads": [
                {
                    "type": "balanced",
                    "position": [0, 0, 0],
                    "size": 10,
                    "name": "Strike Force Alpha"
                },
                {
                    "type": "archer",
                    "position": [-20, 20, 0],
                    "size": 8,
                    "name": "Ranger Squad"
                },
                {
                    "type": "grenadier",
                    "position": [20, -20, 0],
                    "size": 5,
                    "name": "Demo Team"
                }
            ],
            "enemy_waves": [
                {
                    "trigger": "time",
                    "trigger_time": 0,
                    "squads": [
                        {
                            "type": "gromflomite",
                            "position": [200, 200, 0],
                            "size": 15,
                            "name": "Federation Guards",
                            "group": "command_post"
                        },
                        {
                            "type": "turret",
                            "position": [150, 150, 0],
                            "size": 4,
                            "name": "Defense Turrets",
                            "group": "turrets"
                        }
                    ]
                },
                {
                    "trigger": "time",
                    "trigger_time": 300,  # 5 minutes in
                    "squads": [
                        {
                            "type": "gromflomite_elite",
                            "position": [250, 250, 0],
                            "size": 8,
                            "name": "Elite Guard"
                        }
                    ]
                },
                {
                    "trigger": "time",
                    "trigger_time": 600,  # 10 minutes in
                    "squads": [
                        {
                            "type": "gromflomite_commander",
                            "position": [0, 300, 0],
                            "size": 1,
                            "name": "Federation Commander"
                        },
                        {
                            "type": "gromflomite",
                            "position": [50, 300, 0],
                            "size": 20,
                            "name": "Final Reinforcements"
                        }
                    ]
                }
            ]
        }
        
        # Add new missions to the list
        missions.append(cronenberg_mission)
        missions.append(blood_ridge_mission)

        # For each mission in our list
        for mission_data in missions:
            # Save to file
            filepath = os.path.join(self.missions_dir, f"{mission_data['mission_id']}.json")
            with open(filepath, 'w') as f:
                json.dump(mission_data, f, indent=2)
                
            print(f"Created default mission: {mission_data['name']}")
    
    def start_mission(self, mission_id: str, game_state) -> bool:
        """
        Start a specific mission
        
        Args:
            mission_id: ID of the mission to start
            game_state: GameState object to configure
            
        Returns:
            True if mission started successfully, False otherwise
        """
        if mission_id not in self.missions:
            print(f"Mission not found: {mission_id}")
            return False
            
        mission = self.missions[mission_id]
        self.current_mission = mission
        
        # Set up the game state for this mission
        mission.setup_game_state(game_state)
        
        print(f"Started mission: {mission.name}")
        return True
    
    def update(self, game_state, dt: float) -> None:
        """
        Update the current mission
        
        Args:
            game_state: Current game state
            dt: Time elapsed since last frame
        """
        if self.current_mission:
            self.current_mission.update(game_state, dt)
            
            # Check for mission completion
            if self.current_mission.check_win_condition(game_state):
                self._handle_mission_complete()
            elif self.current_mission.check_loss_condition(game_state):
                self._handle_mission_failed()
    
    def _handle_mission_complete(self) -> None:
        """Handle mission completion"""
        if self.current_mission:
            mission_id = self.current_mission.mission_id
            
            # Add to completed missions if not already there
            if mission_id not in self.completed_missions:
                self.completed_missions.append(mission_id)
                
            print(f"Mission completed: {self.current_mission.name}")
            
            # TODO: Trigger mission completion sequence
            # For now, we'll just set current_mission to None
            self.current_mission = None
    
    def _handle_mission_failed(self) -> None:
        """Handle mission failure"""
        if self.current_mission:
            print(f"Mission failed: {self.current_mission.name}")
            
            # TODO: Trigger mission failure sequence
            # For now, we'll just set current_mission to None
            self.current_mission = None
    
    def get_mission_list(self) -> List[Dict]:
        """
        Get a list of all available missions
        
        Returns:
            List of mission info dictionaries
        """
        mission_list = []
        
        for mission_id, mission in self.missions.items():
            mission_list.append({
                'id': mission_id,
                'name': mission.name,
                'description': mission.description,
                'completed': mission_id in self.completed_missions
            })
            
        return mission_list
