import pygame
import random
import data.scripts.text as text
import os
import json
import data.scripts.spritesheet_loader as spritesheet_loader

# Init and screen

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(64)
WINDOW_SIZE = (900, 540)
screen = pygame.display.set_mode(WINDOW_SIZE, pygame.DOUBLEBUF + pygame.RESIZABLE + pygame.SCALED)
pygame.display.set_caption("Platformer")
old_screen = screen.copy()
transparent_screen = screen.copy()
screen_transparency = 0

# Images
play_button1 = pygame.transform.scale(pygame.image.load('data/images/play button1.png').convert(), (149, 72))
play_button2 = pygame.transform.scale(pygame.image.load('data/images/play button2.png').convert(), (149, 72))
background_img1 = pygame.transform.scale(pygame.image.load('data/images/background1.png').convert(), (900, 600))
background_img2 = pygame.transform.scale(pygame.image.load('data/images/background2.png').convert(), (900, 600))
background = background_img1.copy()
player_img = pygame.transform.scale(pygame.image.load('data/images/player/player.png').convert_alpha(), (28, 56))
null_img = pygame.transform.scale(pygame.image.load('data/images/null.png').convert_alpha(), (32, 32))
menu_img = pygame.transform.scale(pygame.image.load('data/images/menu.png').convert(), (900, 540))
icon = pygame.transform.scale(pygame.image.load('icon.ico').convert(), (32, 32))

tile_index = {"null": null_img, }

for entry in os.scandir("data/images/spritesheets"):
    # noinspection PyUnresolvedReferences
    if (entry.path.endswith(".png") or entry.path.endswith(".jpg") or entry.path.endswith(".PNG") or entry.path.endswith(".JPG")) and entry.is_file():
        # noinspection PyUnresolvedReferences
        path = "data/images/spritesheets/" + entry.name
        _, tile_index = spritesheet_loader.load_spritesheet(path, tile_index)

pygame.display.set_icon(icon)

# Font
you_lost_text = text.Font("./data/fonts/large_font.png", (140, 0, 0), (0, 0, 0), 7, )
button_font1 = text.Font("./data/fonts/large_font.png", (69, 116, 150), (0, 0, 0), 5, )
button_font2 = text.Font("./data/fonts/large_font.png", (79, 126, 160), (0, 0, 0), 5, )
twilyte_phaser_font = text.Font("./data/fonts/large_font.png", (63, 63, 116), (0, 0, 0), 6, )

# Colors
bg_color = (15, 15, 15)


# Loads animation into a dictionary
def load_animation(_path, frame_durations, anim_frames):
    animation_name = _path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = _path + '/' + animation_frame_id + '.png'
        animation_image = pygame.image.load(img_loc).convert()
        animation_image = pygame.transform.scale(animation_image, (animation_image.get_width() * 2, animation_image.get_height() * 2))
        animation_image.set_colorkey((0, 0, 0))
        anim_frames[animation_frame_id] = animation_image.copy()
        for _ in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data


def change_action(action_var, frame, new_value):
    if not action_var == new_value:
        action_var = new_value
        frame = 0
    return action_var, frame


# Player class
class Player(pygame.rect.Rect):
    def __init__(self, x=0, y=0, ):
        self.entity_type = "player"
        self.cast = False
        self.cast_timer = 0
        self.immunity = 0
        self.health = 9
        self.decimal_x = x
        self.decimal_y = y
        self.velocity = [0.0, 0.0]
        self.speed = [2.0, 0.5]
        self.max_speed = [5, 12]  # change later if falling long distances still feels floaty, if you increase it make camera follow player a bit quicker
        self.air_timer = 0
        self.movement = {"up": False, "down": False, "right": False, "left": False}
        self.collisions = {'top': False, 'bottom': False, 'right': False, 'left': False}
        self.action = "idle"
        self.frame = 0
        self.flip = False
        self.blitted = False
        self.animation_frames = {}
        self.animation_database = {"jump": [load_animation("./data/images/player/jump", [12, 12, 500], self.animation_frames), (0, 0), (4, 0)],
                                   "run": [load_animation("./data/images/player/run", [5, 5, 5, 5, 5, 5, 5, 5], self.animation_frames), (11, 2), (12, 0)],
                                   "idle": [load_animation("./data/images/player/idle", [20, 20, 20], self.animation_frames), (0, 0), (0, 0)],
                                   "fall": [load_animation("./data/images/player/fall", [5, 5, 5, 5, 5, 5, 5, 5, 5], self.animation_frames), (8, 12), (12, 11)],
                                   "cast_jump": [load_animation("./data/images/player/cast_jump", [12, 12, 500], self.animation_frames), (0, 0), (4, 0)],
                                   "cast_run": [load_animation("./data/images/player/cast_run", [5, 5, 5, 5, 5, 5, 5, 5], self.animation_frames), (11, 2), (12, 0)],
                                   "cast_idle": [load_animation("./data/images/player/cast_idle", [5, 5, 5, 5, 5, 5, 5, 5], self.animation_frames), (18, 0), (0, 0)],
                                   "cast_fall": [load_animation("./data/images/player/cast_fall", [5, 5, 5, 5, 5, 5, 5, 5], self.animation_frames), (8, 12), (12, 11)]
                                   }
        super().__init__(x, y, 14 * 2, 29 * 2)# ADD SPRITESHEETS for animations


class GroundEnemy(pygame.rect.Rect):
    def __init__(self, pos_x=0, pos_y=0, size_x=0, size_y=0, mob_layer="0"):
        self.entity_type = "skeleton"
        self.health = 1
        self.decimal_x = pos_x
        self.decimal_y = pos_y
        self.velocity = [0.0, 0.0]
        self.speed = [1.0, 0.5]
        self.max_speed = [2.5, 12]
        self.movement = {"up": False, "down": False, "right": False, "left": False}
        self.collisions = {'top': False, 'bottom': False, 'right': False, 'left': False}
        self.action = "idle"
        self.frame = 0
        self.flip = False
        self.animation_frames = {}
        self.animation_database = {}
        self.mob_layer = mob_layer
        super().__init__(pos_x, pos_y, size_x * 2, size_y * 2)

    def update_entity(self):
        self.movement = {"up": False, "down": False, "right": False, "left": False}
        if player.decimal_x > self.decimal_x + 5:
            self.movement["right"] = True
            self.flip = False
        elif player.decimal_x < self.decimal_x - 5:
            self.movement["left"] = True
            self.flip = True

        if player.decimal_y * 1.3 < self.decimal_y and self.collisions["bottom"]:
            self.velocity[1] = -12

        # Moves enemies
        move_entity(self, tile_rects, 1)
        # Stops y movement when enemy collides with ground
        if self.collisions["bottom"]:
            self.velocity[1] = 0

        # Run animation
        if self.collisions["bottom"] and self.velocity[0] > 0 * dt:
            self.action, self.frame = change_action(self.action, self.frame, "run")
        elif self.collisions["bottom"] and self.velocity[0] < 0 * dt:
            self.action, self.frame = change_action(self.action, self.frame, "run")
        # Idle animation
        if self.collisions["bottom"] and self.velocity[0] == 0:
            self.action, self.frame = change_action(self.action, self.frame, "idle")
        # Fall animation
        if self.velocity[1] > 0 and self.velocity[1] > 2:
            if "fall" in self.animation_database:
                self.action, self.frame = change_action(self.action, self.frame, "fall")


class Skeleton(GroundEnemy):
    def __init__(self, pos_x=0, pos_y=0, size_x=26, size_y=28, mob_layer="0"):
        GroundEnemy.__init__(self, pos_x, pos_y, size_x, size_y, mob_layer)
        self.entity_type = "skeleton"
        self.health = 1
        self.decimal_x = pos_x
        self.decimal_y = pos_y
        self.velocity = [0.0, 0.0]
        self.speed = [1.0, 0.5]
        self.max_speed = [2.5, 12]
        self.movement = {"up": False, "down": False, "right": False, "left": False}
        self.collisions = {'top': False, 'bottom': False, 'right': False, 'left': False}
        self.action = "idle"
        self.frame = 0
        self.flip = False
        self.animation_frames = {}
        self.animation_database = {"idle": [load_animation("./data/images/skeleton/idle", [20, 20, 20], self.animation_frames), (0, 0), (0, 0)],
                                   "attack": [load_animation("./data/images/skeleton/attack", [20, 20, 20, 20, 20], self.animation_frames), (0, 14), (0, 0)],
                                   "run": [load_animation("./data/images/skeleton/run", [6, 6, 6, 6, 6, 6, 6, 6], self.animation_frames), (8, 2), (0, 0)],
                                   "fall": [load_animation("./data/images/skeleton/fall", [100, ], self.animation_frames), (4, 14), (0, 20)],
                                   }


class Scorpion(GroundEnemy):
    def __init__(self, pos_x=0, pos_y=0, size_x=11, size_y=9, mob_layer="0"):
        GroundEnemy.__init__(self, pos_x, pos_y, size_x, size_y, mob_layer)
        self.entity_type = "skeleton"
        self.health = 1
        self.decimal_x = pos_x
        self.decimal_y = pos_y
        self.velocity = [0.0, 0.0]
        self.speed = [3.0, 0.5]
        self.max_speed = [2.5, 12]
        self.movement = {"up": False, "down": False, "right": False, "left": False}
        self.collisions = {'top': False, 'bottom': False, 'right': False, 'left': False}
        self.action = "idle"
        self.frame = 0
        self.flip = False
        self.animation_frames = {}
        self.animation_database = {"idle": [load_animation("./data/images/scorpion/idle", [20, 20, 20, 20, 20], self.animation_frames), (0, 0), (0, 0)],
                                   "attack": [load_animation("./data/images/scorpion/attack", [20, 20, 20, 20], self.animation_frames), (0, 14), (0, 0)],
                                   "run": [load_animation("./data/images/scorpion/run", [6, 6, 6, 6, ], self.animation_frames), (8, 2), (0, 0)],
                                   }


class Spider(GroundEnemy):
    def __init__(self, pos_x=0, pos_y=0, size_x=11, size_y=9, mob_layer="0"):
        GroundEnemy.__init__(self, pos_x, pos_y, size_x, size_y, mob_layer)
        self.entity_type = "skeleton"
        self.health = 1
        self.decimal_x = pos_x
        self.decimal_y = pos_y
        self.velocity = [0.0, 0.0]
        self.speed = [3.0, 0.5]
        self.max_speed = [2.5, 12]
        self.movement = {"up": False, "down": False, "right": False, "left": False}
        self.collisions = {'top': False, 'bottom': False, 'right': False, 'left': False}
        self.action = "idle"
        self.frame = 0
        self.flip = False
        self.animation_frames = {}
        self.animation_database = {"idle": [load_animation("./data/images/spider/run", [20], self.animation_frames), (0, 46), (0, 0)],
                                   "attack": [load_animation("./data/images/spider/run", [20], self.animation_frames), (0, 46), (0, 0)],
                                   "run": [load_animation("./data/images/spider/run", [5, 5, 5, 5, 5, 5], self.animation_frames), (0, 46), (0, 0)],
                                   }


def load_json_map(_path, _tile_index, ):
    """Loads a json map"""
    f = open(_path)
    g_map = json.load(f)
    f.close()
    rect_list = []
    _twilight_flag = pygame.Rect(32, 32, 32, 32)
    for chunk_ in g_map["map"].values():
        for _tile in chunk_:
            for _layer in chunk_[_tile]:
                _pos = _tile.split(";")
                if not chunk_[_tile][_layer][0][0:5] == "decor":
                    if chunk_[_tile][_layer][0][0:5] == "flag":
                        _twilight_flag = pygame.Rect(int(_pos[0]) * 32, int(_pos[1]) * 32, _tile_index[chunk_[_tile][0]].get_width(),
                                                     _tile_index[chunk_[_tile][0]].get_height())
                    else:
                        rect_list.append(pygame.Rect(int(_pos[0]) * 32, int(_pos[1]) * 32, _tile_index[chunk_[_tile][_layer][0]].get_width(),
                                                     _tile_index[chunk_[_tile][_layer][0]].get_height()))
    return g_map, rect_list, _twilight_flag


# Player
true_scroll = [100, 0]
mouse = pygame.mouse.get_pos()

# Menu
menu_frame = 0
menu_animation_frames = {}
menu_animation_database = {
    "menu": [load_animation("./data/images/menu/menu", [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
                                                        6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
                                                        6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6], menu_animation_frames), (0, 0), (0, 0)]}

# Game map
CHUNK_SIZE = 8

invis_tile_index = ["i", "0"]

for image_path in os.listdir("data/images/tiles"):
    # create the full input path and read the file
    input_path = os.path.join("data/images/", image_path)
    path = image_path.split(".")[0]
    tile_index[path] = pygame.image.load("data/images/tiles/" + image_path).convert()
    tile_index[path] = pygame.transform.scale(tile_index[path], (tile_index[path].get_width() * 2, tile_index[path].get_height() * 2))
    tile_index[image_path.split(".")[0]].set_colorkey((0, 0, 0))

image_list = []

# Starts first level
level = 0

world = "normal"
game_map1, tile_rects1, twilight_flag1 = load_json_map("data/maps/a_" + str(level) + ".json", tile_index, )
game_map2, tile_rects2, twilight_flag2 = load_json_map("data/maps/twilight_" + str(level) + ".json", tile_index, )
game_map = game_map1

layer_dict1 = {}
layer_dict2 = {}

# Creates a surface for each layer in map1
for layer in game_map1["all_layers"]:
    layer_dict1[str(layer)] = pygame.Surface(WINDOW_SIZE)
    layer_dict1[str(layer)].set_colorkey(bg_color)
# Creates a surface for each layer in map2
for layer in game_map1["all_layers"]:
    layer_dict2[str(layer)] = pygame.Surface(WINDOW_SIZE)
    layer_dict2[str(layer)].set_colorkey(bg_color)
layer_dict = layer_dict1

tile_rects = tile_rects1
twilight_flag = twilight_flag1
player_pos = [512, 480]
player = Player(x=player_pos[0], y=player_pos[1])
true_scroll = [0, 0]
scroll = []

# Mobs
mob_creation_dict = {"skeleton": Skeleton, "scorpion": Scorpion, "spider": Spider}
mob_list1 = []
mob_list2 = []
# Loop through the "mobs" tab inside the map, appending all mobs to mob_list
# Mobs are stored like tiles, you need to loop through chunks, tiles, and layers to get to the mobs
for chunk in game_map1["mobs"].values():
    for tile in chunk:
        for layer_ in chunk[tile]:
            if chunk[tile][layer_][0][6:] in mob_creation_dict:
                # If mob string is in mob_creation_dict, add that mob to mob_list
                pos = tile.split(";")
                pos = [int(pos[0]), int(pos[1])]
                layer_ = str(layer_)
                mob_list1.append(mob_creation_dict[chunk[tile][layer_][0][6:]](pos_x=pos[0] * 32, pos_y=pos[1] * 32, mob_layer=layer_))

for chunk in game_map2["mobs"].values():
    for tile in chunk:
        for layer_ in chunk[tile]:
            if chunk[tile][layer_][0][6:] in mob_creation_dict:
                # If mob string is in mob_creation_dict, add that mob to mob_list
                pos = tile.split(";")
                pos = [int(pos[0]), int(pos[1])]
                mob_list2.append(mob_creation_dict[chunk[tile][layer_][0][6:]](pos_x=pos[0] * 32, pos_y=pos[1] * 32, mob_layer=layer_))

mob_list = mob_list1.copy()

# Time
clock = pygame.time.Clock()  # Clock
FPS = 60

# Sound
jump_sounds = [pygame.mixer.Sound("data/sfx/jump_0.wav"), pygame.mixer.Sound("data/sfx/jump_1.wav"), pygame.mixer.Sound("data/sfx/jump_2.wav")]
for i in jump_sounds:
    jump_sounds[jump_sounds.index(i)].set_volume(0.3)
player_hurt_sounds = [pygame.mixer.Sound("data/sfx/hurt_0.wav"), pygame.mixer.Sound("data/sfx/hurt_1.wav"), pygame.mixer.Sound("data/sfx/hurt_2.wav")]
for i in player_hurt_sounds:
    player_hurt_sounds[player_hurt_sounds.index(i)].set_volume(0.3)
cast_sound = pygame.mixer.Sound("data/sfx/cast.wav")
cast_sound.set_volume(0.15)

pygame.mixer.music.load("data/music/music.mp3")


# pygame.mixer.music.play(-1)  # Plays song forever


def draw_button(font1, font2, _text, surf, loc, num=0):
    width = font1.width(_text)
    height = font1.height(_text)
    positions = {"top": loc[1], "left": loc[0], "bottom": loc[1] + height, "right": loc[0] + width}
    if positions["left"] <= mouse[0] <= positions["right"] and positions["bottom"] - num >= mouse[1] >= positions["top"]:
        font2.render(_text, surf, loc)
    else:
        font1.render(_text, surf, loc)
    return positions


def collision_test(entity, tiles):
    hit_list = []
    for _tile in tiles:
        if _tile.colliderect(entity):
            hit_list.append(_tile)
    return hit_list


def move_entity(entity, tiles, num_of_collision_checks=1):
    entity.collisions = {'top': False, 'bottom': False, 'right': False, 'left': False}
    for _ in range(num_of_collision_checks):
        # Increases right velocity
        if entity.movement["right"]:
            if entity.velocity[0] <= entity.max_speed[0]:
                entity.velocity[0] += (entity.speed[0] / num_of_collision_checks) * dt
        # Increases left velocity
        if entity.movement["left"]:
            if entity.velocity[0] >= -entity.max_speed[0]:
                entity.velocity[0] += (-entity.speed[0] / num_of_collision_checks) * dt

        # If entity stops moving right stop movement
        if not entity.movement["right"] and not entity.movement["left"] and entity.velocity[0] > 0:
            if entity.velocity[0] < 1 * dt:
                entity.velocity[0] = 0
            else:
                entity.velocity[0] += -entity.speed[0] * dt

        # If entity stops moving left stop movement
        elif not entity.movement["left"] and not entity.movement["right"] and entity.velocity[0] < 0:
            if entity.velocity[0] > -1 * dt:
                entity.velocity[0] = 0
            else:
                entity.velocity[0] += entity.speed[0] * dt

        entity.decimal_x += (entity.velocity[0] / num_of_collision_checks) * dt
        entity.x = entity.decimal_x
        # Left and right collisions
        hit_list = collision_test(entity, tiles)

        for _tile in hit_list:
            if entity.decimal_x < _tile.x:
                entity.right = _tile.left
                entity.decimal_x = entity.x  #
                entity.collisions['right'] = True
                entity.velocity[0] = 0

            elif entity.decimal_x > _tile.x:
                entity.left = _tile.right
                entity.decimal_x = entity.x
                entity.collisions['left'] = True
                entity.velocity[0] = 0
        if entity.collisions["right"] or entity.collisions["left"]:
            entity.velocity[0] = 0

        # Moves entity up and down
        if entity.velocity[1] <= entity.max_speed[1]:
            entity.velocity[1] += (entity.speed[1] / num_of_collision_checks) * dt
        entity.decimal_y += (entity.velocity[1] / num_of_collision_checks) * dt
        entity.y = entity.decimal_y
        if entity.velocity[1] > 0:
            entity.movement["down"] = True
            entity.movement["up"] = False
        elif entity.velocity[1] < 0:
            entity.movement["up"] = True
            entity.movement["down"] = False
        # Top and bottom collisions
        hit_list = collision_test(entity, tiles)
        for _tile in hit_list:

            if entity.movement["up"]:
                entity.top = _tile.bottom
                entity.decimal_y = entity.y
                entity.collisions['top'] = True
                entity.velocity[1] = 0
            elif entity.movement["down"]:
                entity.bottom = _tile.top
                entity.decimal_y = entity.y
                entity.collisions['bottom'] = True
                entity.movement["down"] = False


# Game state
game_state = "menu"
running = True
while running:

    # GAME STATE:
    if game_state == "game":  # Game state------------------------------------------------------------------------------

        dt = clock.tick(60) / 1000.0
        dt *= 60
        if dt < 1:
            dt = 1
        elif dt > 3:
            dt = 3
        screen.blit(background, (0, 0))
        # Player movement
        pressed = pygame.key.get_pressed()
        move_entity(player, tile_rects, 1)

        player.movement = {"up": False, "down": False, "right": False, "left": False}

        # Stops player from falling when player collides with bottom tile
        if player.collisions["bottom"]:
            player.velocity[1] = 0
            player.air_timer = 0

        else:
            player.air_timer += 1 * dt

        # Stops player when both keys are being held down
        if pressed[pygame.K_d] and pressed[pygame.K_a]:
            if player.velocity[0] > 0:
                player.velocity[0] += -player.speed[0] * dt
                if player.velocity[0] < 1:
                    player.velocity[0] = 0
            elif player.velocity[0] < 0:
                player.velocity[0] += player.speed[0] * dt
                if player.velocity[0] > -1:
                    player.velocity[0] = 0

        # Moves player right
        elif pressed[pygame.K_d]:
            player.movement["right"] = True
            player.flip = False
        # Moves player left
        elif pressed[pygame.K_a]:
            player.movement["left"] = True
            player.flip = True

        # Run animation
        if player.collisions["bottom"] and player.velocity[0] > 0.6 * dt:
            if player.cast:
                player.action, player.frame = change_action(player.action, player.frame, "cast_run")
            else:
                player.action, player.frame = change_action(player.action, player.frame, "run")
        if player.collisions["bottom"] and player.velocity[0] < -0.6 * dt:
            if player.cast:
                player.action, player.frame = change_action(player.action, player.frame, "cast_run")
            else:
                player.action, player.frame = change_action(player.action, player.frame, "run")
        # Idle animation
        if player.collisions["bottom"] and player.velocity[0] == 0:
            if player.cast:
                player.action, player.frame = change_action(player.action, player.frame, "cast_idle")
            else:
                player.action, player.frame = change_action(player.action, player.frame, "idle")
        # Fall animation
        if player.velocity[1] > 0 and player.velocity[1] > 2:
            if player.cast:
                player.action, player.frame = change_action(player.action, player.frame, "cast_fall")
            else:
                player.action, player.frame = change_action(player.action, player.frame, "fall")

        true_scroll[0] += ((player.decimal_x - true_scroll[0] - 436) / 20) * dt
        true_scroll[1] += ((player.decimal_y - true_scroll[1] - 320) / 15) * dt
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        for event in pygame.event.get():
            # Closes game
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:  # switches worlds
                    if world == "twilight":
                        game_map = game_map1
                        tile_rects = tile_rects1
                        twilight_flag = twilight_flag1
                        background = background_img1.copy()
                        layer_dict = layer_dict1
                        mob_list = mob_list1
                        world = "normal"
                    elif world == "normal":
                        game_map = game_map2
                        tile_rects = tile_rects2
                        twilight_flag = twilight_flag2
                        background = background_img2.copy()
                        layer_dict = layer_dict2
                        mob_list = mob_list2
                        world = "twilight"
                    player.cast = True
                    player.cast_timer = 0
                    cast_sound.play()

                # Jump
                if event.key == pygame.K_SPACE:
                    if player.air_timer < 6:
                        player.movement["up"] = True
                        player.velocity[1] = -12
                        jump_sounds[random.randint(0, 2)].play()
            if player.velocity[1] < 0:
                if player.cast:
                    player.action, player.frame = change_action(player.action, player.frame, "cast_jump")
                else:
                    player.action, player.frame = change_action(player.action, player.frame, "jump")
        if player.cast:
            player.cast_timer += 1
            if player.cast_timer > 120:
                player.cast = False
                player.cast_timer = 0

        if player.immunity > 0:
            player.immunity -= 1
        if player.colliderect(twilight_flag):
            level += 1
            if level == 5:
                game_state = "win"
            else:
                world = "normal"
                background = background_img1.copy()
                game_map1, tile_rects1, twilight_flag1 = load_json_map("data/maps/world_" + str(level) + ".json", tile_index, )
                game_map2, tile_rects2, twilight_flag2 = load_json_map("data/maps/twilight_" + str(level) + ".json", tile_index, )
                game_map = game_map1
                tile_rects = tile_rects1
                twilight_flag = twilight_flag1
                player = Player(x=player_pos[0], y=player_pos[1])
                true_scroll = [0, 0]

        # --Blitting--

        # Animations for player

        player.frame += 1
        if player.frame >= len(player.animation_database[player.action][0]):
            player.frame = 0
        player_img_id = player.animation_database[player.action][0][player.frame]
        player.img = player.animation_frames[player_img_id]

        # Erases all layers
        for i in layer_dict:
            layer_dict[i].fill(bg_color)
        # Blits map objects onto layers
        for _y in range(5):
            for _x in range(6):
                target_x = _x - 1 + int(round(scroll[0] / (CHUNK_SIZE * 32)))
                target_y = _y - 1 + int(round(scroll[1] / (CHUNK_SIZE * 32)))
                target_chunk = str(target_x) + ';' + str(target_y)
                if target_chunk in game_map["map"]:
                    for tile in game_map["map"][target_chunk]:
                        for layer in game_map["map"][target_chunk][tile]:
                            pos = tile.split(";")
                            pos[0], pos[1], = int(pos[0]), int(pos[1])
                            if str(game_map["map"][target_chunk][tile][layer][0]) in tile_index:
                                layer_dict[layer].blit((tile_index[game_map["map"][target_chunk][tile][layer][0]]), (pos[0] * 32 - scroll[0], pos[1] * 32 - scroll[1]))
                            else:
                                layer_dict[layer].blit((tile_index["null"]), (pos[0] * 32 - scroll[0], pos[1] * 32 - scroll[1]))
        for enemy in mob_list:  # draw hitboxes
            # pygame.draw.rect(screen, (255, 0, 255), (player.x - scroll[0] - player.animation_database[player.action][1][0],
            #                                          player.y - scroll[1] - player.animation_database[player.action][1][1], player.width, player.height), 1)
            # pygame.draw.rect(screen, (255, 0, 255), (enemy.x - scroll[0] - enemy.animation_database[enemy.action][1][0],
            #                                          enemy.y - scroll[1] - enemy.animation_database[enemy.action][1][1], enemy.width, enemy.height), 1)
            if enemy.colliderect(player):
                if player.immunity <= 0:
                    player.health -= 1
                    player.immunity = 60
                    player_hurt_sounds[random.randint(0, 2)].play()
            enemy.update_entity()

            # Blits enemies
            enemy.frame += 1
            if enemy.frame >= len(enemy.animation_database[enemy.action][0]):
                enemy.frame = 0
            enemy_img_id = enemy.animation_database[enemy.action][0][enemy.frame]
            enemy.img = enemy.animation_frames[enemy_img_id]
            layer_dict[enemy.mob_layer].blit(pygame.transform.flip(enemy.img, enemy.flip, False),
                                             (enemy.decimal_x - scroll[0] - enemy.animation_database[enemy.action][1][0] - enemy.animation_database[enemy.action][2][0],
                                              enemy.decimal_y - scroll[1] - enemy.animation_database[enemy.action][1][1] - enemy.animation_database[enemy.action][2][
                                                  1]))

        layer_dict["0"].blit(pygame.transform.flip(player.img, player.flip, False),
                             (player.decimal_x - true_scroll[0] - player.animation_database[player.action][1][0] - player.animation_database[player.action][2][0],
                              player.decimal_y - scroll[1] - player.animation_database[player.action][1][1] - player.animation_database[player.action][2][1]))
        # Blits all layers
        for i in layer_dict:
            screen.blit(layer_dict[i], (0, 0))

        # Kills player
        if player.health <= 0:
            game_state = "lose"
            pygame.mixer.stop()
            old_screen = screen.copy()
            transparent_screen = pygame.surface.Surface((old_screen.get_width(), old_screen.get_height())).convert_alpha()
            screen_transparency = 0

    elif game_state == "menu":  # Menu state------------------------------------------------------------------------------------------------------------------------
        clock.tick(60)
        menu_frame += 1
        if menu_frame >= len(menu_animation_database["menu"][0]):
            menu_frame = 0
        menu_img_id = menu_animation_database["menu"][0][menu_frame]
        menu_img = menu_animation_frames[menu_img_id]
        screen.blit(menu_img, (0, 0))

        mouse = pygame.mouse.get_pos()
        play_button = draw_button(button_font1, button_font2, "PLAY", screen, (382, 260))
        twilyte_phaser_font.render("Twilyte Phaser", screen, (165, 60))
        if play_button["left"] <= mouse[0] <= play_button["right"] and play_button["bottom"] >= mouse[1] >= play_button["top"]:
            screen.blit(play_button2, (382, 260))
        else:
            screen.blit(play_button1, (382, 260))

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_button["left"] <= mouse[0] <= play_button["right"] and play_button["bottom"] >= mouse[1] >= play_button["top"]:
                    game_state = "game"
                    menu_frame = 0
                    menu_img_id = []

            if event.type == pygame.QUIT:
                running = False

    elif game_state == "lose":  # Lose state----------------------------------------------------------------------------

        clock.tick(60)
        if screen_transparency < 240:
            screen_transparency += 4
        screen.blit(old_screen, (0, 0))
        transparent_screen.fill((0, 0, 0, screen_transparency))
        screen.blit(transparent_screen, (0, 0))

        mouse = pygame.mouse.get_pos()
        you_lost_text.render("Game Over", screen, (271, 150))
        lose_button = draw_button(button_font1, button_font2, "Continue?", screen, (275, 280))

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if lose_button["left"] <= mouse[0] <= lose_button["right"] and lose_button["bottom"] >= mouse[1] >= lose_button["top"]:
                    game_state = "game"
                    world = "normal"
                    game_map1, tile_rects1, twilight_flag1 = load_json_map("data/maps/world_" + str(level) + ".json", tile_index, )
                    game_map2, tile_rects2, twilight_flag2 = load_json_map("data/maps/twilight_" + str(level) + ".json", tile_index, )
                    game_map = game_map1
                    tile_rects = tile_rects1
                    twilight_flag = twilight_flag1
                    player = Player(x=1000, y=480)
                    true_scroll = [0, 0]

            if event.type == pygame.QUIT:
                running = False

    elif game_state == "win":  # Lose state----------------------------------------------------------------------------
        clock.tick(60)
        menu_frame += 1
        if menu_frame >= len(menu_animation_database["menu"][0]):
            menu_frame = 0
        menu_img_id = menu_animation_database["menu"][0][menu_frame]
        menu_img = menu_animation_frames[menu_img_id]
        screen.blit(menu_img, (0, 0))

        mouse = pygame.mouse.get_pos()
        twilyte_phaser_font.render("Thanks for playing!", screen, (93, 60))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

    pygame.display.update()
