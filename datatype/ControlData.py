class ControlData:
    def __init__(self):
        self.steer_scheme = 0
        self.steer_setpoint = 0
        self.prop_scheme = 0
        self.prop_setpoint = 0


    def __repr__(self):
        return (
            'SScheme:{s_scheme}, SSetpt:{s_point},PScheme:{p_scheme}, PSetpt:{p_point}'.format(
                s_scheme=self.steer_scheme, s_point=self.steer_setpoint, p_scheme=self.prop_scheme,
                p_point=self.prop_setpoint
            )
        )