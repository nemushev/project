from pygame import *
from random import randint

# подгружаем отдельно функции для работы со шрифтом
font.init()
font1 = font.Font(None, 80)
win_text = font1.render('YOU WIN!', True, (0, 255, 0))
lose_text = font1.render('YOU LOSE!', True, (255, 0, 0))

font2 = font.Font(None, 36)
font_big = font.Font(None, 50)

# фоновая музыка
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

# нам нужны такие картинки:
img_back = "окно1.jpg"  # фон игры
img_bullet = "пуля.png"  # пуля
img_hero = "кт.png"  # герой

score = 0  # сбито кораблей
goal = 10  # столько кораблей нужно сбить для победы
lost = 0  # пропущено кораблей
max_lost = 3  # проиграли, если пропустили столько

# НОВЫЕ РАЗМЕРЫ (увеличенные)
HERO_WIDTH = 120  # было 80
HERO_HEIGHT = 150  # было 100
ENEMY_WIDTH = 70  # было 80
ENEMY_HEIGHT = 100  # было 50
BULLET_WIDTH = 45  # было 35
BULLET_HEIGHT = 75  # было 60


# класс-родитель для других спрайтов
class GameSprite(sprite.Sprite):
    # конструктор класса
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        # вызываем конструктор класса (Sprite):
        super().__init__()

        # каждый спрайт должен хранить свойство image - изображение
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed

        # каждый спрайт должен хранить свойство rect - прямоугольник, в который он вписан
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    # метод, отрисовывающий героя на окне
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Enemy(GameSprite):
    # движение врага
    def update(self):
        self.rect.y += self.speed
        global lost
        # исчезает, если дойдёт до края экрана
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost = lost + 1


# класс главного игрока
class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.shots_fired = 0  # счетчик выстрелов
        self.reload_time = 0  # время перезарядки
        self.reload_delay = 2000  # задержка перезарядки в миллисекундах (2 секунды)
        self.max_shots_before_reload = 5  # максимальное количество выстрелов до перезарядки

    # метод для управления спрайтом стрелками клавиатуры
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - HERO_WIDTH - 5:  # обновлено с учетом нового размера
            self.rect.x += self.speed
            # класс спрайта-пули

    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 35, 60, -15)
        bullets.add(bullet)
        self.shots_fired += 1
        if self.shots_fired >= self.max_shots_before_reload:
            self.reload_time = 20


class Bullet(GameSprite):
    # движение врага
    def update(self):
        self.rect.y += self.speed
        # исчезает, если дойдет до края экрана
        if self.rect.y < 0:
            self.kill()


def show_result_window(is_win):
    """Функция отображения окна результата игры"""
    # Полупрозрачный фон
    overlay = Surface((win_width, win_height))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    window.blit(overlay, (0, 0))

    if is_win:
        result_text = font1.render('VICTORY!', True, (0, 255, 0))
        message_text = font2.render('You destroyed all enemies!', True, (200, 255, 200))
    else:
        result_text = font1.render('DEFEAT!', True, (255, 0, 0))
        message_text = font2.render('You lost too many ships...', True, (255, 200, 200))

    # Отображаем результат
    result_rect = result_text.get_rect(center=(win_width // 2, win_height // 2 - 80))
    window.blit(result_text, result_rect)

    # Отображаем сообщение
    msg_rect = message_text.get_rect(center=(win_width // 2, win_height // 2 - 20))
    window.blit(message_text, msg_rect)

    # Отображаем статистику
    stats_text = font2.render(f'Score: {score}  |  Lost: {lost}', True, (255, 255, 255))
    stats_rect = stats_text.get_rect(center=(win_width // 2, win_height // 2 + 20))
    window.blit(stats_text, stats_rect)

    # Кнопки
    restart_btn = font_big.render('RESTART', True, (0, 255, 0))
    restart_rect = restart_btn.get_rect(center=(win_width // 2 - 100, win_height // 2 + 80))
    window.blit(restart_btn, restart_rect)

    quit_btn = font_big.render('QUIT', True, (255, 0, 0))
    quit_rect = quit_btn.get_rect(center=(win_width // 2 + 100, win_height // 2 + 80))
    window.blit(quit_btn, quit_rect)

    display.update()

    # Ожидание нажатия на кнопку
    waiting = True
    while waiting:
        for ev in event.get():
            if ev.type == QUIT:
                return False  # Выход из игры
            if ev.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = ev.pos
                if restart_rect.collidepoint(mouse_x, mouse_y):
                    return True  # Перезапуск
                if quit_rect.collidepoint(mouse_x, mouse_y):
                    return False  # Выход из игры
            if ev.type == KEYDOWN:
                if ev.key == K_r:
                    return True  # Перезапуск по клавише R
                if ev.key == K_ESCAPE or ev.key == K_q:
                    return False  # Выход по ESC или Q
    return False


# создаём окошко
win_width = 700
win_height = 500
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))

# Основной игровой цикл
game_running = True
while game_running:
    # создаём спрайты с новыми размерами
    ship = Player(img_hero, (win_width - HERO_WIDTH) // 2, win_height - HERO_HEIGHT - 20,
                  HERO_WIDTH, HERO_HEIGHT, 10)
    ship.last_time = time.get_ticks()  # для отслеживания времени
    img_enemy = ["враг.png", "враг2.png"]

    # создание группы спрайтов-врагов с новыми размерами
    monsters = sprite.Group()
    for i in range(1, 6):
        num = randint(0, len(img_enemy) - 1)
        monster = Enemy(img_enemy[num], randint(ENEMY_WIDTH, win_width - ENEMY_WIDTH),
                        -ENEMY_HEIGHT, ENEMY_WIDTH, ENEMY_HEIGHT, randint(1, 5))
        monsters.add(monster)

    bullets = sprite.Group()

    # переменная "игра закончилась": как только там True, в основном цикле перестают работать спрайты
    finish = False
    run = True

    # основной цикл игры:
    while run:
        # событие нажатия на кнопку Закрыть
        for e in event.get():
            if e.type == QUIT:
                run = False
                game_running = False
            # событие нажатия на пробел - спрайт стреляет
            elif e.type == KEYDOWN:
                if e.key == K_SPACE and not finish:
                    if ship.reload_time <= 0:
                        ship.fire()  # если выстрел произошел
                        fire_sound.play()

        # сама игра: действия спрайтов, проверка правил игры, перерисовка
        if not finish and run:
            # обновляем фон
            window.blit(background, (0, 0))

            # производим движения спрайтов
            ship.update()
            monsters.update()
            bullets.update()

            # обновляем их в новом местоположении при каждой итерации цикла
            ship.reset()
            monsters.draw(window)
            bullets.draw(window)

            # проверка столкновения пули и монстров (и монстр, и пуля при касании исчезают)
            collides = sprite.groupcollide(monsters, bullets, True, True)
            for c in collides:
                # этот цикл повторится столько раз, сколько монстров подбито
                num = randint(0, len(img_enemy) - 1)
                score = score + 1
                monster = Enemy(img_enemy[num], randint(ENEMY_WIDTH, win_width - ENEMY_WIDTH),
                                -ENEMY_HEIGHT, ENEMY_WIDTH, ENEMY_HEIGHT, randint(1, 5))
                monsters.add(monster)

            # проверка выигрыша: сколько очков набрали?
            if score >= goal:
                finish = True
                # Показываем окно победы
                restart = show_result_window(True)
                if not restart:
                    run = False
                    game_running = False
                else:
                    # Сброс игры
                    break

            # возможный проигрыш: пропустили слишком много или герой столкнулся с врагом
            if sprite.spritecollide(ship, monsters, False) or lost >= max_lost:
                finish = True
                # Показываем окно поражения
                restart = show_result_window(False)
                if not restart:
                    run = False
                    game_running = False
                else:
                    # Сброс игры
                    break

            # пишем текст на экране
            text = font2.render("Счет: " + str(score), 1, (255, 255, 255))
            window.blit(text, (10, 20))

            text_lose = font2.render("Пропущено: " + str(lost), 1, (255, 255, 255))
            window.blit(text_lose, (10, 50))
            # показываем информацию о выстрелах и перезарядке
            shots_left = ship.max_shots_before_reload - ship.shots_fired
            if ship.reload_time > 0:
                reload_text = font2.render("ПЕРЕЗАРЯДКА...", 1, (255, 0, 0))
                window.blit(reload_text, (10, 80))
                ship.reload_time -= 1
                ship.shots_fired = 0
            else:
                shots_text = font2.render("Выстрелов осталось: " + str(shots_left), 1, (0, 255, 0))
                window.blit(shots_text, (10, 80))

            display.update()

        time.delay(50)

    # Сброс переменных для новой игры
    if run:  # только если вышли не через закрытие окна
        score = 0
        lost = 0
        ship.shots_fired = 0  # сбрасываем счетчик выстрелов при перезапуске
        ship.reload_time = 0
        for b in bullets:
            b.kill()
        for m in monsters:
            m.kill()
        time.delay(500)  # небольшая задержка перед новым раундом

time.delay(50)
quit()