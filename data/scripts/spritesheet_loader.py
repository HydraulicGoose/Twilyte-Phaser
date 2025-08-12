import pygame


def clip(surf, _x, _y, x_size, y_size):
    handle_surf = surf.copy()
    clip_rect = pygame.Rect(_x, _y, x_size, y_size)
    handle_surf.set_clip(clip_rect)
    image = surf.subsurface(handle_surf.get_clip())
    return image.copy()


def load_spritesheet(path, _tile_index):
    row_content = {}
    _tile_index_copy = {}
    rows = []
    spritesheet = pygame.image.load(path).convert()
    spritesheet.set_colorkey((0, 0, 0))
    name = path.split("/")[-1].split(".")[0]
    # looks down and stores the positions of all pink pixels in row variable
    for _y in range(spritesheet.get_height()):
        c = spritesheet.get_at((0, _y))
        c = (c[0], c[1], c[2])
        if c == (255, 0, 255):
            rows.append(_y)
    _i = 0
    for row in rows:
        row_content = {}
        # Looks to the right until it finds a pink pixel
        for _x in range(spritesheet.get_width()):
            c = spritesheet.get_at((_x, row))
            c = (c[0], c[1], c[2])
            if c == (255, 0, 255):  # found tile
                # Looks to the right of pink pixel for a blue one
                _x2 = 0
                while True:
                    _x2 += 1
                    c = spritesheet.get_at((_x + _x2, row))
                    c = (c[0], c[1], c[2])
                    if c == (0, 255, 255):
                        break
                # Looks to the bottom of the blue pixel until it finds another blue pixel
                _y2 = 0
                while True:
                    _y2 += 1
                    c = spritesheet.get_at((_x2, row + _y2))
                    c = (c[0], c[1], c[2])
                    if c == (0, 255, 255):
                        break
                # Cuts image out and adds it to the list
                img = clip(spritesheet, _x + 1, row + 1, _x2 - 1, _y2 - 1)
                img = pygame.transform.scale(img, (img.get_width() * 2, img.get_height() * 2))
                img.set_colorkey((255, 255, 255))
                row_content[name + str(_i)] = img
                _i += 1
        # spritesheet_images[name] = row_content  # Saves each row into its own list\
        _tile_index.update(row_content)
    return row_content, _tile_index


if __name__ == "__main__":
    # Init
    pygame.init()
    screen = pygame.display.set_mode((1600, 1000))  # Creates the screen
    spritesheet1 = pygame.image.load("./images/test.png").convert_alpha()
    color = (0, 0, 0)
    x, y, x2, y2, = 0, 0, 0, 0
    repeat = True
    mouse_collision = False
    render_list = []
    remove_list = []

    def draw_outline(rect, _color):
        pygame.draw.line(screen, _color, (rect.l_x, rect.l_y), (rect.l_x2, rect.l_y))
        pygame.draw.line(screen, _color, (rect.l_x, rect.l_y), (rect.l_x, rect.l_y2))
        pygame.draw.line(screen, _color, (rect.l_x2, rect.l_y2), (rect.l_x2, rect.l_y))
        pygame.draw.line(screen, _color, (rect.l_x, rect.l_y2), (rect.l_x2, rect.l_y2))

    class SelectedImage(pygame.rect.Rect):
        def __init__(self, l_x, l_y, l_x2, l_y2):
            self.l_x = l_x
            self.l_y = l_y
            self.l_x2 = l_x2
            self.l_y2 = l_y2
            super().__init__((self.l_x2 + 1, self.l_y + 1), (self.l_x - self.l_x2 - 1, self.l_y2 - self.l_y - 1))


    selected_image = SelectedImage(0, 0, 0, 0)
    running = True
    while running:
        screen.fill((25, 25, 25))
        screen.blit(pygame.transform.scale(spritesheet1, (spritesheet1.get_width() * 4, spritesheet1.get_height() * 4)),#cutting images out will set them to 4x resolution
                    (0, 0))
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_collision = False
                for r in render_list:
                    if r.collidepoint(mouse):
                        selected_image = r
                        mouse_collision = True
                if not mouse_collision:
                    try:
                        selected_image = SelectedImage(0, 0, 0, 0)
                        color = screen.get_at(mouse)
                        color = (color[0], color[1], color[2])
                        if not color == (25, 25, 25):
                            # Moves up until it finds a gray pixel
                            selected_image.l_y = mouse[1]
                            while True:
                                selected_image.l_y += -1
                                color = screen.get_at((mouse[0], selected_image.l_y))
                                color = (color[0], color[1], color[2])
                                if color == (25, 25, 25):
                                    break
                            # Moves down until it finds a graselected_image.l_y pixel
                            selected_image.l_y2 = mouse[1]
                            while True:
                                selected_image.l_y2 += 1
                                color = screen.get_at((mouse[0], selected_image.l_y2))
                                color = (color[0], color[1], color[2])
                                if color == (25, 25, 25):
                                    break
                            # Moves right until it finds a gray pixel
                            selected_image.l_x = mouse[0]
                            while True:
                                selected_image.l_x += 1
                                color = screen.get_at((selected_image.l_x, int((selected_image.l_y + selected_image.l_y2) / 2)))
                                color = (color[0], color[1], color[2])
                                if color == (25, 25, 25):
                                    break
                            # Moves left until it finds a gray pixel
                            selected_image.l_x2 = mouse[0]
                            while True:
                                selected_image.l_x2 += -1
                                color = screen.get_at((selected_image.l_x2, int((selected_image.l_y + selected_image.l_y2) / 2)))
                                color = (color[0], color[1], color[2])
                                if color == (25, 25, 25):
                                    break

                            while True:
                                repeat = False
                                # Checks up in a vertical line and if non-gray pixels it moves up and checks again
                                selected_image.l_x3 = selected_image.l_x2
                                while True:
                                    selected_image.l_x3 += 1
                                    color = screen.get_at((selected_image.l_x3, selected_image.l_y))
                                    color = (color[0], color[1], color[2])
                                    if not color == (25, 25, 25):
                                        repeat = True
                                        selected_image.l_x3 = selected_image.l_x2
                                        selected_image.l_y += -1
                                    if color == (25, 25, 25) and selected_image.l_x3 == selected_image.l_x:
                                        break
                                # Checks down in a vertical line and if non-gray pixels it moves down and checks again
                                selected_image.l_x3 = selected_image.l_x2
                                while True:
                                    selected_image.l_x3 += 1
                                    color = screen.get_at((selected_image.l_x3, selected_image.l_y2))
                                    color = (color[0], color[1], color[2])
                                    if not color == (25, 25, 25):
                                        repeat = True
                                        selected_image.l_x3 = selected_image.l_x2
                                        selected_image.l_y2 += 1
                                    if color == (25, 25, 25) and selected_image.l_x3 == selected_image.l_x:
                                        break
                                # Checks right in a horizontal line, if non-gray pixels it moves right and checks again
                                selected_image.l_y3 = selected_image.l_y
                                while True:
                                    selected_image.l_y3 += 1
                                    color = screen.get_at((selected_image.l_x, selected_image.l_y3))
                                    color = (color[0], color[1], color[2])
                                    if not color == (25, 25, 25):
                                        repeat = True
                                        selected_image.l_y3 = selected_image.l_y
                                        selected_image.l_x += 1
                                    if color == (25, 25, 25) and selected_image.l_y3 == selected_image.l_y2:
                                        break
                                # Checks left in a horizontal line, if non-gray pixels it moves left and checks again
                                selected_image.l_y3 = selected_image.l_y
                                while True:
                                    selected_image.l_y3 += 1
                                    color = screen.get_at((selected_image.l_x2, selected_image.l_y3))
                                    color = (color[0], color[1], color[2])
                                    if not color == (25, 25, 25):
                                        repeat = True
                                        selected_image.l_y3 = selected_image.l_y
                                        selected_image.l_x2 += -1
                                    if color == (25, 25, 25) and selected_image.l_y3 == selected_image.l_y2:
                                        break

                                if not repeat:
                                    break

                            for r in render_list:
                                if r.colliderect(selected_image):
                                    remove_list.append(r)
                            # (self.l_x2 + 1, self.l_y + 1), (self.l_x - self.l_x2 - 1, self.l_y2 - self.l_y - 1)
                            selected_image.x, selected_image.y, = selected_image.l_x2 + 1, selected_image.l_y + 1# fix this the rect needs to be bigger
                            render_list.append(selected_image)
                            if len(remove_list) > 0:
                                for r in remove_list:
                                    render_list.remove(r)
                                remove_list = []
                            render_list.append(selected_image)
                    except IndexError:
                        pass

            # Stops program when window closes
            if event.type == pygame.QUIT:
                running = False
        for i in render_list:
            draw_outline(i, (255, 255, 0))
        draw_outline(selected_image, (255, 0, 255))

        pygame.display.update()
