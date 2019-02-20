import random
import arcade


# Main parameters of the game:
field_width = 17  # In tiles. Keep it odd. The default is 17.
field_height = 15  # In tiles. Keep it odd. The default is 15.
pause_allowed = False

# Fixing main parameters:
if field_width < 7: field_width = 7
if field_width % 2 == 0: field_width += 1
if field_height < 3: field_height = 3
if field_height % 2 == 0: field_height += 1

# Other parameters:
tile_width = 30
screen_width = field_width * tile_width + tile_width * 2
if screen_width < 460: screen_width = 460
screen_height = field_height * tile_width + tile_width * 2 + 30
screen_title = 'Snake'

max_score = field_width * field_height - 3

# Generate wall coordinates:
wall_coordinates = []
x = tile_width / 2  # Starting at the left bottom corner.
y = tile_width / 2
for _ in range(field_height + 2):  # Going up.
    wall_coordinates.append((x, y))
    y += tile_width
x += tile_width
y -= tile_width
for _ in range(field_width + 1):  # Going right.
    wall_coordinates.append((x, y))
    x += tile_width
x -= tile_width
y -= tile_width
for _ in range(field_height + 1):  # Going down.
    wall_coordinates.append((x, y))
    y -= tile_width
x -= tile_width
y += tile_width
for _ in range(field_width):  # Going left.
    wall_coordinates.append((x, y))
    x -= tile_width

# Generate field coordinates:
n = 30
field_coordinates = []
field_coordinates_light_green = []
field_coordinates_green = []
i = 0
for x in range(1, field_width + 1):
    for y in range(1, field_height + 1):
        field_coordinates.append((n*x + tile_width/2, n*y + tile_width/2))
        if i % 2 == 0:
            field_coordinates_light_green.append((n*x + tile_width/2, n*y + tile_width/2))
        else:
            field_coordinates_green.append((n*x + tile_width/2, n*y + tile_width/2))
        i += 1


class MyGame(arcade.Window):
    """ Main application class. """
    def create_tail(self, x, y, angle):
        tail = arcade.Sprite('tail.png')
        tail.center_x = x
        tail.center_y = y
        tail.angle = angle
        self.tail_list.append(tail)

    def tail_end(self, x, y, angle):
        self.tail_end_list[0].kill()
        tail_end = arcade.Sprite('tail_end.png')
        tail_end.center_x = x
        tail_end.center_y = y
        tail_end.angle = angle
        self.tail_end_list.append(tail_end)

    def death(self):
        if self.score > self.high_score:
            self.high_score = self.score
        self.setup()
        self.dead = True

    def __init__(self, width, height, title):
        """ Initializer. """
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK_BEAN)
        self.wall_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()

        # Generate walls:
        for x, y in wall_coordinates:
            wall = arcade.Sprite('wall.png')
            wall.center_x = x
            wall.center_y = y
            self.wall_list.append(wall)

        # Generate background:
        for x, y in field_coordinates_light_green:
            tile = arcade.Sprite('light_green.png')
            tile.center_x = x
            tile.center_y = y
            self.background_list.append(tile)
        for x, y in field_coordinates_green:
            tile = arcade.Sprite('green.png')
            tile.center_x = x
            tile.center_y = y
            self.background_list.append(tile)

        self.score = 0
        self.high_score = 0

    def setup(self):
        ''' Reset. '''
        self.game_paused = True
        self.game_state = 'START'

        # Resetting sprite lists:
        self.player_list = arcade.SpriteList()
        self.tail_list = arcade.SpriteList()
        self.tail_end_list = arcade.SpriteList()
        self.apples_list = arcade.SpriteList()

        y = field_height * tile_width / 2 + tile_width

        # Head:
        self.head = arcade.Sprite('head.png')
        self.head.center_x = 165
        self.head.center_y = y
        self.head.angle = 0
        self.player_list.append(self.head)

        # Tail:
        tail_end = arcade.Sprite('tail_end.png')
        tail_end.center_x = 75
        tail_end.center_y = y
        tail_end.angle = 0
        self.tail_end_list.append(tail_end)
        self.create_tail(105, y, 0)
        self.create_tail(135, y, 0)

        # First apple:
        self.apple = arcade.Sprite('apple.png')
        self.apple.center_x = 225
        self.apple.center_y = y
        self.apples_list.append(self.apple)

        # Misc:
        self.frame_count = 0
        self.actions_q = []
        self.dead = False
        self.direction = 'RIGHT'
        self.freeze_tail_end = False

    def on_draw(self):
        ''' Render. '''
        arcade.start_render()

        # Draw sprites:
        self.background_list.draw()
        self.player_list.draw()
        self.tail_list.draw()
        self.tail_end_list.draw()
        self.apples_list.draw()
        self.wall_list.draw()
        text_y = (field_height+2) * tile_width + 8
        arcade.draw_text("Score: {}".format(self.score), 35, text_y, arcade.color.WHITE)
        arcade.draw_text("High score: {}".format(self.high_score), 165, text_y, arcade.color.WHITE)
        arcade.draw_text("Max score: {}".format(max_score), 325, text_y, arcade.color.WHITE)

    def on_key_press(self, key, modifiers):
        ''' A key was pressed. '''
        if key == arcade.key.SPACE:
            if self.game_state == 'START':
                self.game_state = 'IN_PROGRESS'
                self.score = 0
                self.game_paused = False
            else:
                if pause_allowed:
                    if self.game_paused:
                        self.game_paused = False
                    else:
                        self.game_paused = True
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
        ''' Movement and game logic. '''
        if not self.game_paused:
            self.frame_count += 1
            if self.frame_count % 18 == 0:  # Simulated "slow" frame.
                if self.dead:
                    self.actions_q = []
                    self.dead = False

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
                    self.apple = arcade.Sprite('apple.png')
                    self.to_remove = [(tail.center_x, tail.center_y) for tail in self.tail_list] \
                                      + [(self.head.center_x, self.head.center_y)]
                    self.to_remove.append((self.tail_end_list[0].center_x, self.tail_end_list[0].center_y))
                    self.field_coordinates_for_apple = [xy for xy in field_coordinates if xy not in self.to_remove]
                    self.apple.center_x, self.apple.center_y = random.choice(self.field_coordinates_for_apple)
                    self.apples_list.append(self.apple)

                    # Changing the color of the tail end after eating an apple:
                    x = self.tail_end_list[0].center_x
                    y = self.tail_end_list[0].center_y
                    angle = self.tail_end_list[0].angle
                    self.tail_end_list[0].kill()
                    tail_end_frozen = arcade.Sprite('tail_end_frozen.png')
                    tail_end_frozen.center_x = x
                    tail_end_frozen.center_y = y
                    tail_end_frozen.angle = angle
                    self.tail_end_list.append(tail_end_frozen)


def main():
    """ Main method. """
    window = MyGame(screen_width, screen_height, screen_title)
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()
