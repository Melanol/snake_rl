import os
import random
import arcade


# Main game parameters:
FIELD_WIDTH = 17  # In tiles. Keep it odd. Min: 7. Default: 17.
FIELD_HEIGHT = 15  # In tiles. Keep it odd. Min: 3. Default: 15.
SPEED = 1  # Min: 1. Max: 17. Default: 1. Integers only.
PAUSE_ALLOWED = True

# Fixing main parameters:
if FIELD_WIDTH < 7: FIELD_WIDTH = 7
if FIELD_WIDTH % 2 == 0: FIELD_WIDTH += 1
if FIELD_HEIGHT < 3: FIELD_HEIGHT = 3
if FIELD_HEIGHT % 2 == 0: FIELD_HEIGHT += 1
if SPEED < 1: SPEED = 1
elif SPEED > 17: SPEED = 17
frames_per_turn = 18 - SPEED

# Other parameters:
TILE_WIDTH = 30
SCREEN_WIDTH = FIELD_WIDTH * TILE_WIDTH + TILE_WIDTH * 2
if SCREEN_WIDTH < 460: SCREEN_WIDTH = 460
SCREEN_HEIGHT = FIELD_HEIGHT * TILE_WIDTH + TILE_WIDTH * 2 + 30
SCREEN_TITLE = 'Snake RL'

max_score = FIELD_WIDTH * FIELD_HEIGHT - 3

# Generate wall coordinates:
wall_coordinates = []
x = TILE_WIDTH / 2  # Starting at the left bottom corner.
y = TILE_WIDTH / 2
for _ in range(FIELD_HEIGHT + 2):  # Going up.
    wall_coordinates.append((x, y))
    y += TILE_WIDTH
x += TILE_WIDTH
y -= TILE_WIDTH
for _ in range(FIELD_WIDTH + 1):  # Going right.
    wall_coordinates.append((x, y))
    x += TILE_WIDTH
x -= TILE_WIDTH
y -= TILE_WIDTH
for _ in range(FIELD_HEIGHT + 1):  # Going down.
    wall_coordinates.append((x, y))
    y -= TILE_WIDTH
x -= TILE_WIDTH
y += TILE_WIDTH
for _ in range(FIELD_WIDTH):  # Going left.
    wall_coordinates.append((x, y))
    x -= TILE_WIDTH

# Generate field coordinates:
n = 30
field_coordinates = []
field_coordinates_light_green = []
field_coordinates_green = []
i = 0
for x in range(1, FIELD_WIDTH + 1):
    for y in range(1, FIELD_HEIGHT + 1):
        field_coordinates.append((n * x + TILE_WIDTH / 2, n * y + TILE_WIDTH / 2))
        if i % 2 == 0:
            field_coordinates_light_green.append((n * x + TILE_WIDTH / 2, n * y + TILE_WIDTH / 2))
        else:
            field_coordinates_green.append((n * x + TILE_WIDTH / 2, n * y + TILE_WIDTH / 2))
        i += 1


class Snake_RL(arcade.Window):
    def __init__(self, width, height, title):
        """ Initializer. """
        super().__init__(width, height, title)
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        arcade.set_background_color(arcade.color.BLACK_BEAN)
        self.wall_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()

        # Generate walls:
        for x, y in wall_coordinates:
            wall = arcade.Sprite('sprites/wall.png', center_x=x, center_y=y)
            self.wall_list.append(wall)

        # Generate background:
        for x, y in field_coordinates_light_green:
            tile = arcade.Sprite('sprites/light_green.png', center_x=x, center_y=y)
            self.background_list.append(tile)
        for x, y in field_coordinates_green:
            tile = arcade.Sprite('sprites/green.png', center_x=x, center_y=y)
            self.background_list.append(tile)

        self.score = 0
        self.high_score = 0

    def create_tail(self, x, y, angle):
        tail = arcade.Sprite('sprites/tail.png', center_x=x, center_y=y)
        tail.angle = angle
        self.tail_list.append(tail)

    def tail_end(self, x, y, angle):
        self.tail_end_list[0].kill()
        tail_end = arcade.Sprite('sprites/tail_end.png', center_x=x, center_y=y)
        tail_end.angle = angle
        self.tail_end_list.append(tail_end)

    def death(self):
        if self.score > self.high_score:
            self.high_score = self.score
        self.game_paused = True
        self.game_state = 'DEAD'

    def setup(self):
        """ Reset. """
        self.game_paused = True
        self.game_state = 'START'

        # Resetting sprite lists:
        self.player_list = arcade.SpriteList()
        self.tail_list = arcade.SpriteList()
        self.tail_end_list = arcade.SpriteList()
        self.apples_list = arcade.SpriteList()

        y = FIELD_HEIGHT * TILE_WIDTH / 2 + TILE_WIDTH

        # Head:
        self.head = arcade.Sprite('sprites/head.png', center_x=165, center_y=y)
        self.head.angle = 0
        self.player_list.append(self.head)

        # Tail:
        tail_end = arcade.Sprite('sprites/tail_end.png', center_x=75, center_y=y)
        tail_end.angle = 0
        self.tail_end_list.append(tail_end)
        self.create_tail(105, y, 0)
        self.create_tail(135, y, 0)

        # First apple:
        self.apple = arcade.Sprite('sprites/apple.png', center_x=225, center_y=y)
        self.apples_list.append(self.apple)

        # Misc:
        self.frame_count = 0
        self.actions_q = []
        self.direction = 'RIGHT'
        self.freeze_tail_end = False

    def on_draw(self):
        """ Render. """
        arcade.start_render()

        # Draw sprites:
        self.background_list.draw()
        self.tail_list.draw()
        self.tail_end_list.draw()
        self.apples_list.draw()
        self.wall_list.draw()
        self.player_list.draw()
        text_y = (FIELD_HEIGHT + 2) * TILE_WIDTH + 8
        arcade.draw_text("Score: {}".format(self.score), 10, text_y, arcade.color.WHITE)
        arcade.draw_text("High score: {}".format(self.high_score), 100, text_y, arcade.color.WHITE)
        arcade.draw_text("Max score: {}".format(max_score), 230, text_y, arcade.color.WHITE)
        arcade.draw_text("Speed: {}".format(SPEED), 365, text_y, arcade.color.WHITE)
        if self.game_state == 'START':
            if PAUSE_ALLOWED:
                arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 340, 50, arcade.color.WHITE_SMOKE)
                arcade.draw_text("Press SPACE to start/pause,\n"
                                 "use WASD or ARROWS for navigation", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                 arcade.color.BLACK, 15, align="center",
                                 anchor_x="center", anchor_y="center")
            else:
                arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 340, 50, arcade.color.WHITE_SMOKE)
                arcade.draw_text("Press SPACE to start,\n"
                                 "use WASD or ARROWS for navigation", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                 arcade.color.BLACK, 15, align="center",
                                 anchor_x="center", anchor_y="center")
        elif self.game_state == 'DEAD':
            arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 340, 50, arcade.color.WHITE_SMOKE)
            arcade.draw_text("YOU DIED", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                             arcade.color.BLACK, 15, align="center",
                             anchor_x="center", anchor_y="center")

    def on_key_press(self, key, modifiers):
        """ A key was pressed. """
        if key == arcade.key.SPACE:
            if self.game_state == 'START':
                self.game_state = 'IN_PROGRESS'
                self.score = 0
                self.game_paused = False
            elif self.game_state == 'DEAD':
                self.setup()
            else:
                if PAUSE_ALLOWED:
                    if self.game_paused:
                        self.game_paused = False
                    else:
                        self.game_paused = True
        else:
            if self.game_state != 'START':
                if len(self.actions_q) <= 1:
                    try:
                        if self.actions_q[0] in ['UP', 'DOWN']:
                            if key in [arcade.key.LEFT, arcade.key.A]:
                                self.actions_q.append('LEFT')
                            elif key in [arcade.key.RIGHT, arcade.key.D]:
                                self.actions_q.append('RIGHT')
                        elif self.actions_q[0] in ['LEFT', 'RIGHT']:
                            if key in [arcade.key.UP, arcade.key.W]:
                                self.actions_q.append('UP')
                            elif key in [arcade.key.DOWN, arcade.key.S]:
                                self.actions_q.append('DOWN')
                    except IndexError:  # No actions found / inertial movement
                        if self.direction in ['UP', 'DOWN']:
                            if key in [arcade.key.LEFT, arcade.key.A]:
                                self.actions_q.append('LEFT')
                            elif key in [arcade.key.RIGHT, arcade.key.D]:
                                self.actions_q.append('RIGHT')
                        elif self.direction in ['LEFT', 'RIGHT']:
                            if key in [arcade.key.UP, arcade.key.W]:
                                self.actions_q.append('UP')
                            elif key in [arcade.key.DOWN, arcade.key.S]:
                                self.actions_q.append('DOWN')

    def update(self, delta_time):
        """ Movement and game logic. """
        if not self.game_paused:
            self.frame_count += 1
            if self.frame_count % frames_per_turn == 0:  # Simulated "slow" frame.
                if self.game_state == 'DEAD':
                    self.actions_q = []

                if self.freeze_tail_end:
                    self.freeze_tail_end = False
                else:
                    x = self.tail_list[0].center_x
                    y = self.tail_list[0].center_y
                    angle = self.tail_list[0].angle
                    self.tail_end(x, y, angle)
                    self.tail_list[0].kill()

                last_x = self.head.center_x
                last_y = self.head.center_y

                try:
                    if self.actions_q[0] == 'UP':
                        self.head.center_y += 30
                        self.head.angle = 90
                        tail_angle = 90
                        del self.actions_q[0]
                        self.direction = 'UP'
                    elif self.actions_q[0] == 'DOWN':
                        self.head.center_y -= 30
                        self.head.angle = 270
                        tail_angle = 270
                        del self.actions_q[0]
                        self.direction = 'DOWN'
                    elif self.actions_q[0] == 'RIGHT':
                        self.head.center_x += 30
                        self.head.angle = 0
                        tail_angle = 0
                        del self.actions_q[0]
                        self.direction = 'RIGHT'
                    elif self.actions_q[0] == 'LEFT':
                        self.head.center_x -= 30
                        self.head.angle = 180
                        tail_angle = 180
                        del self.actions_q[0]
                        self.direction = 'LEFT'
                except IndexError:
                    if self.direction == 'UP':
                        self.head.center_y += 30
                        self.head.angle = 90
                        tail_angle = 90
                    elif self.direction == 'DOWN':
                        self.head.center_y -= 30
                        self.head.angle = 270
                        tail_angle = 270
                    elif self.direction == 'RIGHT':
                        self.head.center_x += 30
                        self.head.angle = 0
                        tail_angle = 0
                    elif self.direction == 'LEFT':
                        self.head.center_x -= 30
                        self.head.angle = 180
                        tail_angle = 180

                self.create_tail(last_x, last_y, tail_angle)

                # Collision with walls:
                for wall in self.wall_list:
                    if wall.center_x == self.head.center_x and wall.center_y == self.head.center_y:
                        self.death()
                        return None

                # Collision with itself:
                for tail in self.tail_list:
                    if tail.center_x == self.head.center_x and tail.center_y == self.head.center_y:
                        self.death()
                        return None
                    if self.tail_end_list[0].center_x == self.head.center_x \
                        and self.tail_end_list[0].center_y == self.head.center_y:
                            self.death()
                            return None

                # Collision with apple:
                if self.apple.center_x == self.head.center_x and self.apple.center_y == self.head.center_y:
                    if self.score == max_score:
                        self.death()
                        return None
                    self.freeze_tail_end = True
                    self.score += 1
                    self.apples_list[0].kill()

                    # Generate apple:
                    self.apple = arcade.Sprite('sprites/apple.png')
                    self.to_remove = [(tail.center_x, tail.center_y) for tail in self.tail_list] \
                                      + [(self.head.center_x, self.head.center_y)]
                    self.to_remove.append((self.tail_end_list[0].center_x, self.tail_end_list[0].center_y))
                    self.field_coordinates_for_apple = [xy for xy in field_coordinates if xy not in self.to_remove]
                    if self.score < max_score:
                        self.apple.center_x, self.apple.center_y = random.choice(self.field_coordinates_for_apple)
                        self.apples_list.append(self.apple)

                    # Changing the color of the tail end after eating an apple:
                    x = self.tail_end_list[0].center_x
                    y = self.tail_end_list[0].center_y
                    angle = self.tail_end_list[0].angle
                    self.tail_end_list[0].kill()
                    tail_end_frozen = arcade.Sprite('sprites/tail_end_frozen.png', center_x=x, center_y=y)
                    tail_end_frozen.angle = angle
                    self.tail_end_list.append(tail_end_frozen)

    def get_snake_rl_path(self):
        return self.file_path


def main():
    """ Main method. """
    window = Snake_RL(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()
