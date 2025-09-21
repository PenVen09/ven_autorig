component_lists = {
            "General": {
                "Joints": {
                    "position": [(0, 0, 0)],
                    "rotation": [(0, 0, 0)],
                    "suffix": ["root"],
                    "attrs": {
                        "rigType": {"widget": "string", "value": "Base"},
                        "component_index": {"widget": "float", "value": "0"},
                        "comp_name": {"widget": "string", "value": "Base"},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Right", "Center", "Left"],
                            "value": "Center"
                        },
                        "isBindJoint": {"widget": "bool", "value": True}
                    }
                },
                "FKIKChain": {
                    "position": [(0, 0, 0), (5, 0, 0), (5, 0, 0), (5, 0, 0)],
                    "rotation": [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
                    "suffix": ["chain"],
                    "attrs": {
                        "rigType": {"widget": "string", "value": "FKIKChain"},
                        "comp_name": {"widget": "string", "value": "FKIKChain"},
                        "component_index": {"widget": "float", "value": "0"},
                        "numJoints": {"widget": "float", "value": 3},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Right", "Center", "Left"],
                            "value": "Center"
                        },
                    }
                }
            },
            "Limbs": {
                "Spine":{
                    "position": [(0,0,0)],
                    "rotation": [(0,0,0)],
                    "suffix":["spine"],
                    "attrs":{
                        "rigType": {"widget": "string", "value": "spine"},
                        "comp_name": {"widget": "string", "value": "Spine"},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Right", "Center", "Left"],
                            "value": "Center"}

                    }
                },
                "Shoulder": {
                    "position": [(4, 143, 3), (0, 0, 20)],
                    "rotation": [(0, 102, 0), (0, 0, 0)],
                    "suffix": ["shoulder", "tip"],
                    "attrs": {
                        "rigType": {"widget": "string", "value": "shoulder"},
                        "comp_name": {"widget": "string", "value": "Shoulder"},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Right", "Center", "Left"],
                            "value": "Left"
                    },
                },
            },
                "Arm": {
                    "position": [(23.563, 143, -1.158), (0, 0, -6.948), (58.203, -18.818, 0.699)],
                    "rotation": [(0, 0, -35), (0, 0, 0), (0, 0, 0)],
                    "suffix": ["upperarm", "elbow", "wrist"],
                    "attrs": {
                        "rigType": {"widget": "string", "value": "arm"},
                        "comp_name": {"widget": "string", "value": "Arm"},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Right", "Center", "Left"],
                            "value": "Left"
                        }
                    }
                },
                "Fingers": {
                    "position": [(0,0,0), (5, 0, 0), (5, 0, 0), (5, 0, 0)],
                    "rotation": [(0,0,0), (0,0,0), (0,0,0), (0,0,0)],
                    "suffix": ["finger"],
                    "attrs": {
                        "rigType": {"widget": "string", "value": "finger"},
                        "comp_name": {"widget": "string", "value": "Fingers"},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Right", "Center", "Left"],
                            "value": "Left"
                        }
                    }
                },
                "Leg": {
                    "position": [(22.495, 75.582, 0), (0, 0, 14.255), (0, -64, -10.644)],
                    "rotation": [(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                    "suffix": ["hips", "knee", "ankle"],
                    "attrs": {
                        "rigType": {"widget": "string", "value": "leg"},
                        "comp_name": {"widget": "string", "value": "Leg"},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Right", "Center", "Left"],
                            "value": "Left"
                        }
                    }
                },
                "Foot": {
                    "position": [(22.495, 11.582, 3.611), (0, -5.7, 8.619), (0, -2.108, 8.619)],
                    "rotation": [(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                    "suffix": ["foot", "toe", "toeend"],
                    "attrs": {
                        "rigType": {"widget": "string", "value": "foot"},
                        "comp_name": {"widget": "string", "value": "Foot"},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Right", "Center", "Left"],
                            "value": "Left"}
                    }

                }
            }
        }
