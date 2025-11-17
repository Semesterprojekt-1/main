def turn_in_place(self, direction, degrees):
        """
        Turns the robot around its axis in a given number of degrees
        
        :param direction (STR): The direction we want to turn in.
        :param degrees (INT): Amount of degrees we want to turn.

        """
        circumference = math.pi * 25
        distance = circumference/(360/degrees)
        steps = self.cm_to_steps(distance)
        
        if direction == "right":
            step_seq_len = len(self.left.step_sequence)
            for _ in range(steps):
                for i in range(step_seq_len):
                    self.left.set_step(self.left.step_sequence[i])
                    self.right.set_step(self.right.step_sequence[-i])
            self.stop()
            
        elif direction == "left":
            step_seq_len = len(self.left.step_sequence)
            for _ in range(steps):
                for i in range(step_seq_len):
                    self.left.set_step(self.left.step_sequence[-i])
                    self.right.set_step(self.right.step_sequence[i])
            self.stop()
        else:
            raise ValueError("Must be right or left")
        self.stop()
