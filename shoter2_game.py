from pygame import *
from random import randint

#подгружаем отдельно функции для работы со шрифтом
font.init()
font1 = font.Font(None, 80)
win = font1.render('You Win!', True, (255, 255, 255))
lose = font1.render('You Lose!', True, (180, 0, 0))

font2 = font.Font(None, 36)

#фоновая музыка
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

#нам нужны такие картинки:
img_back = "galaxy.jpg" #фон игры
img_bullet = "bullet.png" #пуля
img_hero = "rocket.png" #герой

score = 0 #сбито кораблей
goal = 10 #столько кораблей нужно сбить для победы
lost = 0 #пропущено кораблей
max_lost = 3 #проиграли, если пропустили столько

# НОВЫЕ РАЗМЕРЫ (увеличенные)
HERO_WIDTH = 120  # было 80
HERO_HEIGHT = 150  # было 100
ENEMY_WIDTH = 100  # было 80
ENEMY_HEIGHT = 70  # было 50
BULLET_WIDTH = 45  # было 35
BULLET_HEIGHT = 75  # было 60

#класс-родитель для других спрайтов
class GameSprite(sprite.Sprite):
    #конструктор класса
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        #вызываем конструктор класса (Sprite):
        super().__init__()
        
        #каждый спрайт должен хранить свойство image - изображение
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        
        #каждый спрайт должен хранить свойство rect - прямоугольник, в который он вписан
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
        
    #метод, отрисовывающий героя на окне
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))
class Enemy(GameSprite):
   #движение врага
   def update(self):
       self.rect.y += self.speed
       global lost
       #исчезает, если дойдёт до края экрана
       if self.rect.y > win_height:
           self.rect.x = randint(80, win_width - 80)
           self.rect.y = 0
           lost = lost + 1
#класс главного игрока
class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.shots_fired = 0  # счетчик выстрелов
        self.reload_time = 0  # время перезарядки
        self.reload_delay = 2000  # задержка перезарядки в миллисекундах (2 секунды)
        self.max_shots_before_reload = 5  # максимальное количество выстрелов до перезарядки
    
    #метод для управления спрайтом стрелками клавиатуры
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - HERO_WIDTH - 5:  # обновлено с учетом нового размера
            self.rect.x += self.speed
            #класс спрайта-пули  
    def fire(self):
       bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 35, 60, -15)
       bullets.add(bullet)

class Bullet(GameSprite):
    # движение врага
    def update(self):
        self.rect.y += self.speed
        # исчезает, если дойдет до края экрана
        if self.rect.y < 0:
            self.kill()
            
#создаём окошко
win_width = 700
win_height = 500
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))

#создаём спрайты с новыми размерами
ship = Player(img_hero, (win_width - HERO_WIDTH)//2, win_height - HERO_HEIGHT - 20, HERO_WIDTH, HERO_HEIGHT, 10)
ship.last_time = time.get_ticks()  # для отслеживания времени
img_enemy = ["asteroid.png","ufo.png"]
#создание группы спрайтов-врагов с новыми размерами
monsters = sprite.Group()
for i in range(1, 6):
    num = randint(0, len(img_enemy)-1)
    monster = Enemy(img_enemy[num], randint(ENEMY_WIDTH, win_width - ENEMY_WIDTH), -ENEMY_HEIGHT, ENEMY_WIDTH, ENEMY_HEIGHT, randint(1, 5))
    monsters.add(monster)
    
bullets = sprite.Group()

#переменная "игра закончилась": как только там True, в основном цикле перестают работать спрайты
finish = False

#основной цикл игры:
run = True #флаг сбрасывается кнопкой закрытия окна
while run:
    #событие нажатия на кнопку Закрыть
    for e in event.get():
        if e.type == QUIT:
            run = False
        #событие нажатия на пробел - спрайт стреляет
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                ship.fire()  # если выстрел произошел
                fire_sound.play()
    
    #сама игра: действия спрайтов, проверка правил игры, перерисовка
    if not finish:
        #обновляем фон
        window.blit(background,(0,0))
        
        #производим движения спрайтов
        ship.update()
        monsters.update()
        bullets.update()
        
        #обновляем их в новом местоположении при каждой итерации цикла
        ship.reset()
        monsters.draw(window)
        bullets.draw(window)
        
        #проверка столкновения пули и монстров (и монстр, и пуля при касании исчезают)
        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            #этот цикл повторится столько раз, сколько монстров подбито
            num = randint(0, len(img_enemy)-1)
            score = score + 1
            monster = Enemy(img_enemy[num], randint(ENEMY_WIDTH, win_width - ENEMY_WIDTH), -ENEMY_HEIGHT, ENEMY_WIDTH, ENEMY_HEIGHT, randint(1, 5))
            monsters.add(monster)
        
        #возможный проигрыш: пропустили слишком много или герой столкнулся с врагом
        if sprite.spritecollide(ship, monsters, False) or lost >= max_lost:
            finish = True #проиграли, ставим фон и больше не управляем спрайтами.
            window.blit(lose, (200, 200))
        
        #проверка выигрыша: сколько очков набрали?
        if score >= goal:
            finish = True
            window.blit(win, (200, 200))
        
        #пишем текст на экране
        text = font2.render("Счет: " + str(score), 1, (255, 255, 255))
        window.blit(text, (10, 20))
        
        text_lose = font2.render("Пропущено: " + str(lost), 1, (255, 255, 255))
        window.blit(text_lose, (10, 50))
        #показываем информацию о выстрелах и перезарядке
        shots_left = ship.max_shots_before_reload - ship.shots_fired
        if ship.reload_time > 0:
            reload_text = font2.render("ПЕРЕЗАРЯДКА...", 1, (255, 0, 0))
            window.blit(reload_text, (10, 80))
        else:
            shots_text = font2.render("Выстрелов осталось: " + str(shots_left), 1, (0, 255, 0))
            window.blit(shots_text, (10, 80))
        
        display.update()
        
    #бонус: автоматический перезапуск игры
    else:
        finish = False
        score = 0
        lost = 0
        ship.shots_fired = 0  # сбрасываем счетчик выстрелов при перезапуске
        ship.reload_time = 0
        for b in bullets:
            b.kill()
        for m in monsters:
            m.kill()
        
        time.delay(3000)
        for i in range(1, 6):
            num = randint(0, len(img_enemy)-1)
            monster = Enemy(img_enemy[num], randint(ENEMY_WIDTH, win_width - ENEMY_WIDTH), -ENEMY_HEIGHT, ENEMY_WIDTH, ENEMY_HEIGHT, randint(1, 5))
            monsters.add(monster)
    
    time.delay(50)