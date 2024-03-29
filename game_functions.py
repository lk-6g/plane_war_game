import sys
import pygame
from bullet import Bullet
import bullet
from alien import Alien
from time import sleep

def check_events(ai_settings, screen, ship, aliens, bullets, stats, play_button, sb, sound):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
            
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, aliens, bullets, stats, sb, sound)
                
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if play_button.rect.collidepoint(mouse_x, mouse_y):
                check_play_button(ai_settings, screen, ship, aliens, bullets, stats, sb)
            
def check_play_button(ai_settings, screen, ship, aliens, bullets, stats, sb):
    if not stats.game_active:
        ai_settings.initialize_dynamic_settings()
        pygame.mouse.set_visible(False)
        
        stats.reset_stats()
        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_remain_ships()
        
        stats.game_active = True
        
        aliens.empty()
        bullets.empty()
        
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()
            
def check_keydown_events(event, ai_settings, screen, ship, aliens, bullets, stats, sb, sound):
    if event.key == pygame.K_d:
        ship.moving_right = True
    elif event.key == pygame.K_a:
        ship.moving_left = True
    elif event.key == pygame.K_KP1:
        fire_bullet(ai_settings, screen, ship, bullets, stats)
        sound.bullet_fire_sound()
    elif event.key == pygame.K_q:
        sys.exit()
    elif event.key == pygame.K_p:
        check_play_button(ai_settings, screen, ship, aliens, bullets, stats, sb)
        
def check_keyup_events(event, ship):
    if event.key == pygame.K_d:
        ship.moving_right = False
    elif event.key == pygame.K_a:
        ship.moving_left = False
    
def update_screen(ai_settings, screen, ship, bullets, aliens, stats, play_button, sb, bg):
    screen.fill(ai_settings.bg_color)
    bg.blitme()
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)
    sb.show_score()
    if not stats.game_active:
        play_button.draw_button()
        
    pygame.display.flip()
    
def update_bullets(ai_settings, screen, ship, aliens, bullets, stats, sb, sound):
    bullets.update()
    for bullet in bullets.copy():
        if bullet.rect.top <= 30:
            bullets.remove(bullet)
            
    check_bullet_alien_collisions(ai_settings, screen, ship, aliens, bullets, stats, sb, sound)
    
def check_bullet_alien_collisions(ai_settings, screen, ship, aliens, bullets, stats, sb, sound):
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
    
    if collisions:
        sound.bullet_alien_sound()
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
        check_high_score(stats, sb)
    
    if len(aliens) == 0:
        bullets.empty()
        
        stats.level += 1
        sb.prep_level()
        
        ai_settings.increase_speed()
        create_fleet(ai_settings, screen, ship, aliens)
        
def check_high_score(stats, sb):
    if stats.high_score < stats.score:
        stats.high_score = stats.score
        write_max_score(stats)
        sb.prep_high_score()
        
def write_max_score(stats):
    filename = 'max_score_history.txt'
    
    with open(filename, 'w') as file_object:
        file_object.write(str(stats.high_score))
            
def fire_bullet(ai_settings, screen, ship, bullets, stats):
    if len(bullets) < ai_settings.bullet_allowed and stats.game_active:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)
        
def create_fleet(ai_settings, screen, ship, aliens):
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    number_aliens_x = get_number_aliens_x(ai_settings, alien_width)
    alien_height = alien.rect.height
    ship_height = ship.rect.height
    number_rows = get_number_rows(ai_settings, alien_height, ship_height)
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_width, alien_number, row_number)
        
def get_number_aliens_x(ai_settings, alien_width):
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (1.2 * alien_width))
    return number_aliens_x
    
def create_alien(ai_settings, screen, aliens, alien_width, alien_number, row_number):
    alien = Alien(ai_settings, screen)
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = 30 + alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)
    
def get_number_rows(ai_settings, alien_height, ship_height):
    available_space_y = ai_settings.screen_height - 3 * alien_height - ship_height
    number_rows = int(available_space_y / (4 * alien_height))
    return number_rows

def update_aliens(ai_settings, screen, ship, aliens, bullets, stats, sb, sound):
    check_fleet_edges(ai_settings, aliens)
    aliens.update()
    
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, screen, ship, aliens, bullets, stats, sb, sound)
        
    check_aliens_bottom(ai_settings, screen, ship, aliens, bullets, stats, sb, sound)
    
def check_fleet_edges(ai_settings, aliens):
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break
        
def change_fleet_direction(ai_settings, aliens):
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1
    
def ship_hit(ai_settings, screen, ship, aliens, bullets, stats, sb, sound):
    sound.explode_sound()
    
    if stats.ships_left > 0:
        stats.ships_left -= 1
        
        sb.prep_remain_ships()
    
        aliens.empty()
        bullets.empty()
    
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()
    
        sleep(2)
        
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)
    
def check_aliens_bottom(ai_settings, screen, ship, aliens, bullets, stats, sb, sound):
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            ship_hit(ai_settings, screen, ship, aliens, bullets, stats, sb, sound)
            break