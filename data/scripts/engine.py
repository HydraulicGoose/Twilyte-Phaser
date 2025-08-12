import pygame
import json


def create_tile_rects(g_map, tile_size):
    tile_rects = []
    for chunk in g_map.values():
        for tile in chunk:
            if tile[1] != "0":
                tile_rects.append(pygame.Rect(int(tile[0][0]) * tile_size,
                                              int(tile[0][1]) * tile_size, tile_size, tile_size))
    return tile_rects


def load_map(path, tile_size):
    # 19 x 25
    # Must be a multiple of 8
    f = open(path + ".txt", "r")
    data = f.read()
    f.close()
    data = data.split("\n")
    g_map = {}
    key = [0, 0]
    tile = [-5, -1]

    for row in data:
        i = 0
        key[0] = -1
        tile[0] = -5  # Offsets terrain so that it renders correctly
        tile[1] += 1

        for char in row:  # Window size 25 x 19
            tile[0] += 1
            i += 1
            if i <= 8:
                if not str(key[0]) + ';' + str(key[1]) in g_map:
                    g_map[str(key[0]) + ';' + str(key[1])] = []
                if str(char) != "0":
                    pos = [[tile[0], tile[1]], char]
                    g_map[str(key[0]) + ';' + str(key[1])].append(pos)
            else:
                i = 1
                key[0] += 1
                if not str(key[0]) + ';' + str(key[1]) in g_map:
                    g_map[str(key[0]) + ';' + str(key[1])] = []
                if str(char) != "0":
                    pos = [[tile[0], tile[1]], char]
                    g_map[str(key[0]) + ';' + str(key[1])].append(pos)
    tile_rects = create_tile_rects(g_map, tile_size)
    return g_map, tile_rects


def load_json_map(path, tile_index):
    f = open(path)
    game_map = json.load(f)
    f.close()
    rect_list = []
    for chunk in game_map.values():
        for tile in chunk:
            # if tile[1] != "invisible": change for tiles with no collision
            rect_list.append(pygame.Rect(int(tile[0][0]) * 32,
                                         int(tile[0][1]) * 32, tile_index[tile[1]].get_width(),
                                         tile_index[tile[1]].get_height()))
    return game_map, rect_list
