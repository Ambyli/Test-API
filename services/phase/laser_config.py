from .config import Config
from .sql_config import SQLConfig


# keyence config
class KeyenceLaserConfig(Config):
    # CONSTRUCTOR
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # # CUSTOMERS
        self.customers = {
            "Default": {
                "Default": {
                    "Default": {
                        "0": {"value": "default", "x": 1, "y": -7, "z": 4, "theta": 0},
                        "1": {"value": "casestep", "x": 0, "y": 0, "z": 0, "theta": 0},
                        "3": {"value": "aligner", "x": 1, "y": -12, "z": 4, "theta": 0},
                        "4": {"value": "default", "x": 1, "y": -2, "z": 4, "theta": 0},
                    }
                },
                "Brius Technol - 1076": {
                    "Default": {
                        "0": {"value": "default", "x": 1, "y": -7, "z": 4, "theta": 0},
                        "1": {
                            "value": "patientbrius",
                            "x": 0,
                            "y": 0,
                            "z": 0,
                            "theta": 0,
                        },
                        "3": {"value": "aligner", "x": 1, "y": -12, "z": 4, "theta": 0},
                        "4": {"value": "default", "x": 1, "y": -2, "z": 4, "theta": 0},
                    }
                },
                "ORTHOFX - 1117": {
                    "Default": {
                        "0": {"value": "default", "x": 1, "y": -7, "z": 4, "theta": 0},
                        "1": {"value": "patient", "x": 0, "y": 0, "z": 0, "theta": 0},
                        "2": {
                            "value": "OrthoFX",
                            "x": 0,
                            "y": 0,
                            "z": 0,
                            "theta": 0,
                            "height": 1.2,
                        },
                        "3": {"value": "aligner", "x": 1, "y": -12, "z": 4, "theta": 0},
                        "4": {"value": "default", "x": 1, "y": -2, "z": 4, "theta": 0},
                    },
                    "OFXSKA": {
                        "0": {"value": "default", "x": 1, "y": -7, "z": 4, "theta": 0},
                        "1": {"value": "name", "x": 0, "y": 0, "z": 0, "theta": 0},
                        "2": {
                            "value": "OrthoFX",
                            "x": 0,
                            "y": 0,
                            "z": 0,
                            "theta": 0,
                            "height": 1.2,
                        },
                        "3": {"value": "aligner", "x": 1, "y": -12, "z": 4, "theta": 0},
                        "4": {"value": "default", "x": 1, "y": -2, "z": 4, "theta": 0},
                    },
                },
                "Six Month 1130": {
                    "Default": {
                        "0": {"value": "default", "x": 1, "y": -7, "z": 4, "theta": 0},
                        "1": {"value": "patient", "x": 0, "y": 0, "z": 0, "theta": 0},
                        "2": {
                            "value": "6MS",
                            "x": 0,
                            "y": 0,
                            "z": 0,
                            "height": 1,
                            "theta": 0,
                        },
                        "3": {"value": "aligner", "x": 1, "y": -12, "z": 4, "theta": 0},
                        "4": {"value": "default", "x": 1, "y": -2, "z": 4, "theta": 0},
                    }
                },
            },
            "Alternate": {
                "Default": {
                    "Default": {
                        "0": {"value": "aligner", "x": 1, "y": -7, "z": 4, "theta": 0},
                        "1": {"value": "casestep", "x": 0, "y": 0, "z": 0, "theta": 0},
                        "3": {"value": "aligner", "x": 1, "y": -12, "z": 4, "theta": 0},
                        "4": {"value": "default", "x": 1, "y": -2, "z": 4, "theta": 0},
                    }
                },
                "Brius Technol - 1076": {
                    "Default": {
                        "0": {"value": "aligner", "x": 1, "y": -7, "z": 4, "theta": 0},
                        "1": {
                            "value": "patientbrius",
                            "x": 0,
                            "y": 0,
                            "z": 0,
                            "theta": 0,
                        },
                        "3": {"value": "aligner", "x": 1, "y": -12, "z": 4, "theta": 0},
                        "4": {"value": "default", "x": 1, "y": -2, "z": 4, "theta": 0},
                    }
                },
                "ORTHOFX - 1117": {
                    "Default": {
                        "0": {"value": "aligner", "x": 1, "y": -7, "z": 4, "theta": 0},
                        "1": {"value": "patient", "x": 0, "y": 0, "z": 0, "theta": 0},
                        "2": {
                            "value": "OrthoFX",
                            "x": 0,
                            "y": 0,
                            "z": 0,
                            "theta": 0,
                            "height": 1.2,
                        },
                        "3": {"value": "aligner", "x": 1, "y": -12, "z": 4, "theta": 0},
                        "4": {"value": "default", "x": 1, "y": -2, "z": 4, "theta": 0},
                    },
                    "OFXSKA": {
                        "0": {"value": "aligner", "x": 1, "y": -7, "z": 4, "theta": 0},
                        "1": {"value": "name", "x": 0, "y": 0, "z": 0, "theta": 0},
                        "2": {
                            "value": "OrthoFX",
                            "x": 0,
                            "y": 0,
                            "z": 0,
                            "theta": 0,
                            "height": 1.2,
                        },
                        "3": {"value": "aligner", "x": 1, "y": -12, "z": 4, "theta": 0},
                        "4": {"value": "default", "x": 1, "y": -2, "z": 4, "theta": 0},
                    },
                },
                "Six Month 1130": {
                    "Default": {
                        "0": {"value": "aligner", "x": 1, "y": -7, "z": 4, "theta": 0},
                        "1": {"value": "patient", "x": 0, "y": 0, "z": 0, "theta": 0},
                        "2": {
                            "value": "6MS",
                            "x": 0,
                            "y": 0,
                            "z": 0,
                            "theta": 0,
                            "height": 1,
                        },
                        "3": {"value": "aligner", "x": 1, "y": -12, "z": 4, "theta": 0},
                        "4": {"value": "default", "x": 1, "y": -2, "z": 4, "theta": 0},
                    }
                },
            },
        }

        # # REQUIRE PLACEMENT
        self.blks_placement = {
            "Default": {
                "Default": {"Default": [1, 2, 3]},
                "ORTHOFX - 1117": {"Default": [1, 2, 3]},
                "Six Month 1130": {"Default": [1, 2, 3]},
            }
        }

        self.keyence_machine_settings = {
            1: {
                "r_line_settings": {
                    "x_offset": -1.5,
                    "y_offset": 4.75,
                    "z_offset": -6.3,
                    "theta_offset": 0,
                },
                "s_line_settings": {
                    "x_offset": 0,
                    "y_offset": 21.5,
                    "z_offset": -9.4,
                    "theta_offset": 0,
                },
                "r_line_blk_offsets": {
                    "0": {"x": 0, "y": -7, "z": -4.7, "theta": 0},
                    "1": {"x": 4, "y": 4, "z": -0.3, "theta": 15},
                    "2": {"x": 1, "y": 1, "z": -1, "theta": -5},
                    "3": {"x": 2, "y": 2, "z": -0.7, "theta": 0},
                    "4": {"x": 0, "y": -7, "z": -2.7, "theta": 0},
                },
                "s_line_blk_offsets": {
                    "0": {"x": 0, "y": 0, "z": 1, "theta": 0},
                    "1": {"x": 2, "y": 2, "z": 2, "theta": 15},
                    "2": {"x": 1, "y": 1, "z": 0, "theta": -5},
                    "3": {"x": 0, "y": 2, "z": 0, "theta": 0},
                    "4": {"x": 0, "y": 0, "z": 2, "theta": 0},
                },
            },
            2: {
                "r_line_settings": {
                    "x_offset": -3.3,
                    "y_offset": 4.5,
                    "z_offset": -6.3,
                    "theta_offset": 0,
                },
                "s_line_settings": {
                    "x_offset": -3,
                    "y_offset": 20,
                    "z_offset": -9.4,
                    "theta_offset": 0,
                },
                "r_line_blk_offsets": {
                    "0": {"x": 0, "y": -7, "z": -4.7, "theta": 0},
                    "1": {"x": 2, "y": 2, "z": 0.2, "theta": 15},
                    "2": {"x": 1, "y": 1, "z": 0.8, "theta": -5},
                    "3": {"x": 2, "y": 2, "z": 0.1, "theta": -5},
                    "4": {"x": 0, "y": -7, "z": -2.7, "theta": 0},
                },
                "s_line_blk_offsets": {
                    "0": {"x": 0, "y": 0, "z": 0, "theta": 0},
                    "1": {"x": 2, "y": 2, "z": 2, "theta": 15},
                    "2": {"x": 1, "y": 1, "z": 0, "theta": -5},
                    "3": {"x": 2, "y": 2, "z": 0, "theta": 0},
                    "4": {"x": 0, "y": 0, "z": 2, "theta": 0},
                },
            },
            12: {
                "r_line_settings": {
                    "x_offset": 0,
                    "y_offset": 4,
                    "z_offset": -6.3,
                    "theta_offset": 0,
                },
                "s_line_settings": {
                    "x_offset": 0,
                    "y_offset": 19.5,
                    "z_offset": -9.4,
                    "theta_offset": 0,
                },
                "r_line_blk_offsets": {
                    "0": {"x": 0, "y": -7, "z": -4.7, "theta": 0},
                    "1": {"x": 2, "y": 2, "z": 0, "theta": 15},
                    "2": {"x": 1, "y": 1, "z": 0, "theta": -5},
                    "3": {"x": 2, "y": 2, "z": 0, "theta": 0},
                    "4": {"x": 0, "y": -7, "z": -2.7, "theta": 0},
                },
                "s_line_blk_offsets": {
                    "0": {"x": 0, "y": 0, "z": 4, "theta": 0},
                    "1": {"x": 2, "y": 2, "z": 2, "theta": 15},
                    "2": {"x": 1, "y": 1, "z": 0, "theta": -5},
                    "3": {"x": 2, "y": 2, "z": 0, "theta": 0},
                    "4": {"x": 0, "y": 0, "z": 2, "theta": 0},
                },
            },
        }

        # # KEYENCE PROFILES
        self.product_laser_settings = {
            1: {
                "ignored_codes": ["T001"],
                "default_profile": "FLX",
                "dynamic_profiles": {
                    "POCA": "FLX",
                    "POCAT": "AT",
                    "POCAR": "RET",
                    "SSCA": "FLX",
                    "SSCAT": "AT",
                    "TSCA": "FLX",
                    "TSR": "RET",
                    "TSCAT": "AT",
                    "SMCA": "FLX",
                    "ZR2": "RET",
                    "SMCAT": "AT",
                    "Z1": "FLX",
                    "Z1AT": "AT",
                    "TBR1": "WRET",
                    "DCA": "FLX",
                    "DCAT": "AT",
                    "DARE": "RET",
                },
                "blk_sizes": {
                    "1": {"height": 1.5, "width": -1},
                    "2": {"height": 1.5, "width": -1},
                    "4": {"height": 1, "width": -1},
                },
                "profiles": {
                    "FLX2": {
                        "0": {
                            "power": 50,
                            "speed": 400,
                            "frequency": 70,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                        "1": {
                            "power": 60,
                            "speed": 500,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 4,
                        },
                        "2": {
                            "power": 60,
                            "speed": 500,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 4,
                        },
                        "3": {
                            "power": 60,
                            "speed": 500,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 4,
                        },
                        "4": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 100,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                    },
                    "FLX": {
                        "0": {
                            "power": 50,
                            "speed": 400,
                            "frequency": 60,
                            "spotvar": -10,
                            "repetition": 7,
                        },
                        "1": {
                            "power": 70,
                            "speed": 170,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "2": {
                            "power": 70,
                            "speed": 170,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "3": {
                            "power": 70,
                            "speed": 170,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "4": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 100,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                    },
                    "WRET": {
                        "0": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                        "1": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                        "2": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                        "3": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                        "4": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 100,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                    },
                    "AT": {
                        "0": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 90,
                            "spotvar": 0,
                            "repetition": 8,
                        },
                        "1": {
                            "power": 80,
                            "speed": 200,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "2": {
                            "power": 80,
                            "speed": 200,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "3": {
                            "power": 80,
                            "speed": 200,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "4": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 100,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                    },
                    "RET": {
                        "0": {
                            "power": 80,
                            "speed": 800,
                            "frequency": 80,
                            "spotvar": 0,
                            "repetition": 12,
                        },
                        "1": {
                            "power": 80,
                            "speed": 100,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "2": {
                            "power": 80,
                            "speed": 100,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "3": {
                            "power": 80,
                            "speed": 100,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "4": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 100,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                    },
                },
            },
            2: {
                "ignored_codes": ["T001"],
                "default_profile": "FLX",
                "dynamic_profiles": {
                    "POCA": "FLX",
                    "POCAT": "AT",
                    "POCAR": "RET",
                    "SSCA": "FLX",
                    "SSCAT": "AT",
                    "TSCA": "FLX",
                    "TSR": "RET",
                    "TSCAT": "AT",
                    "SMCA": "FLX",
                    "ZR2": "RET",
                    "SMCAT": "AT",
                    "Z1": "FLX",
                    "Z1AT": "AT",
                    "TBR1": "WRET",
                    "DCA": "FLX",
                    "DCAT": "AT",
                    "DARE": "RET",
                },
                "blk_sizes": {
                    "1": {"height": 1.5, "width": -1},
                    "2": {"height": 1.5, "width": -1},
                    "4": {"height": 1, "width": -1},
                },
                "profiles": {
                    "FLX2": {
                        "0": {
                            "power": 50,
                            "speed": 400,
                            "frequency": 70,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                        "1": {
                            "power": 60,
                            "speed": 500,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 4,
                        },
                        "2": {
                            "power": 60,
                            "speed": 500,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 4,
                        },
                        "3": {
                            "power": 60,
                            "speed": 500,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 4,
                        },
                        "4": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 100,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                    },
                    "FLX": {
                        "0": {
                            "power": 50,
                            "speed": 400,
                            "frequency": 60,
                            "spotvar": -10,
                            "repetition": 7,
                        },
                        "1": {
                            "power": 70,
                            "speed": 170,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "2": {
                            "power": 70,
                            "speed": 170,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "3": {
                            "power": 70,
                            "speed": 170,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "4": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 100,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                    },
                    "WRET": {
                        "0": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                        "1": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                        "2": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                        "3": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                        "4": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 100,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                    },
                    "AT": {
                        "0": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 90,
                            "spotvar": 0,
                            "repetition": 8,
                        },
                        "1": {
                            "power": 80,
                            "speed": 200,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "2": {
                            "power": 80,
                            "speed": 200,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "3": {
                            "power": 80,
                            "speed": 200,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "4": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 100,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                    },
                    "RET": {
                        "0": {
                            "power": 80,
                            "speed": 800,
                            "frequency": 80,
                            "spotvar": 0,
                            "repetition": 12,
                        },
                        "1": {
                            "power": 80,
                            "speed": 100,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "2": {
                            "power": 80,
                            "speed": 100,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "3": {
                            "power": 80,
                            "speed": 100,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "4": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 100,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                    },
                },
            },
            12: {
                "ignored_codes": ["T001"],
                "default_profile": "FLX",
                "dynamic_profiles": {
                    "POCA": "FLX",
                    "POCAT": "AT",
                    "POCAR": "RET",
                    "SSCA": "FLX",
                    "SSCAT": "AT",
                    "TSCA": "FLX",
                    "TSR": "RET",
                    "TSCAT": "AT",
                    "SMCA": "FLX",
                    "ZR2": "RET",
                    "SMCAT": "AT",
                    "Z1": "FLX",
                    "Z1AT": "AT",
                    "TBR1": "WRET",
                    "DCA": "FLX",
                    "DCAT": "AT",
                    "DARE": "RET",
                },
                "blk_sizes": {
                    "1": {"height": 1.5, "width": -1},
                    "2": {"height": 1.5, "width": -1},
                    "4": {"height": 1, "width": -1},
                },
                "profiles": {
                    "FLX2": {
                        "0": {
                            "power": 50,
                            "speed": 400,
                            "frequency": 70,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                        "1": {
                            "power": 60,
                            "speed": 500,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 4,
                        },
                        "2": {
                            "power": 60,
                            "speed": 500,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 4,
                        },
                        "3": {
                            "power": 60,
                            "speed": 500,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 4,
                        },
                        "4": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 100,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                    },
                    "FLX": {
                        "0": {
                            "power": 50,
                            "speed": 400,
                            "frequency": 60,
                            "spotvar": -10,
                            "repetition": 7,
                        },
                        "1": {
                            "power": 70,
                            "speed": 170,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "2": {
                            "power": 70,
                            "speed": 170,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "3": {
                            "power": 70,
                            "speed": 170,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "4": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 100,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                    },
                    "WRET": {
                        "0": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                        "1": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                        "2": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                        "3": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 50,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                        "4": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 100,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                    },
                    "AT": {
                        "0": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 90,
                            "spotvar": 0,
                            "repetition": 8,
                        },
                        "1": {
                            "power": 80,
                            "speed": 200,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "2": {
                            "power": 80,
                            "speed": 200,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "3": {
                            "power": 80,
                            "speed": 200,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "4": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 100,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                    },
                    "RET": {
                        "0": {
                            "power": 80,
                            "speed": 800,
                            "frequency": 80,
                            "spotvar": 0,
                            "repetition": 12,
                        },
                        "1": {
                            "power": 80,
                            "speed": 100,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "2": {
                            "power": 80,
                            "speed": 100,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "3": {
                            "power": 80,
                            "speed": 100,
                            "frequency": 40,
                            "spotvar": 10,
                            "repetition": 1,
                        },
                        "4": {
                            "power": 60,
                            "speed": 600,
                            "frequency": 100,
                            "spotvar": 0,
                            "repetition": 6,
                        },
                    },
                },
            },
        }

        # # COMMANDS
        self.commands = {
            "default": "SELECT CONCAT(b.CaseNumber, a.Step) as Result FROM {database}.dbo.Aligners as a, {database}.dbo.Cases as b WHERE a.CaseID = b.CaseID and AlignerID = ?",
            "casestep": "SELECT CONCAT(b.CaseNumber, a.Step, ' ', CHAR(CONVERT(INT, FLOOR(RAND()*4+1))%27+64)) as Result FROM {database}.dbo.Aligners as a, {database}.dbo.Cases as b WHERE a.CaseID = b.CaseID and AlignerID = ?",
            "aligner": "SELECT CAST(AlignerID as varchar(25)) as Result FROM {database}.dbo.Aligners WHERE AlignerID = ?",
            "sample": "SELECT CONCAT('Sample ', a.Step) as Result FROM {database}.dbo.Aligners as a, {database}.dbo.Cases as b WHERE a.CaseID = b.CaseID and AlignerID = ?",
            "initials": "SELECT CONCAT(substring(trim(b.PatientLast),0,3) + '.' + substring(trim(b.PatientFirst),0,3), a.Step, ' ', CHAR(CONVERT(INT, FLOOR(RAND()*4+1))%27+64)) as Result FROM {database}.dbo.Aligners as a, {database}.dbo.Cases as b WHERE a.CaseID = b.CaseID and AlignerID = ?",
            "name": "SELECT CONCAT(trim(b.PatientLast), ' ', a.Step, ' ', CHAR(CONVERT(INT, FLOOR(RAND()*4+1))%27+64)) as Result FROM {database}.dbo.Aligners as a, {database}.dbo.Cases as b WHERE a.CaseID = b.CaseID and AlignerID = ?",
            "patient": "SELECT CONCAT(b.RXNumber, ' ', a.Step, ' ', CHAR(CONVERT(INT, FLOOR(RAND()*4+1))%27+64)) as Result FROM {database}.dbo.Aligners as a, {database}.dbo.Cases as b WHERE a.CaseID = b.CaseID and AlignerID = ?",
            "patientbrius": "SELECT CONCAT(SUBSTRING(b.RXNumber, 3, 7), ' ', a.Step, ' ', CHAR(CONVERT(INT, FLOOR(RAND()*4+1))%27+64)) as Result FROM {database}.dbo.Aligners as a, {database}.dbo.Cases as b WHERE a.CaseID = b.CaseID and AlignerID = ?",
            "patientnewline": "SELECT CONCAT(b.RXNumber, CHAR(10), a.Step, ' ', CHAR(CONVERT(INT, FLOOR(RAND()*4+1))%27+64)) as Result FROM {database}.dbo.Aligners as a, {database}.dbo.Cases as b WHERE a.CaseID = b.CaseID and AlignerID = ?",
        }

        # # BLK REMOVAL
        self.blk_removal = {"0": ["height"], "3": ["height"]}
