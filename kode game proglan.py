import pygame
import random
import sys

from handgesture import HandTracker

# =========================
# INIT
# =========================
pygame.init()

WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Expand!")

clock = pygame.time.Clock()
tracker = HandTracker()

# =========================
# COLORS
# =========================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)

# =========================
# ASSETS MANAGEMENT
# =========================
def load_spritesheet(filename, num_frames, width_scale=70, height_scale=90):
    """Memuat spritesheet otomatis untuk Sukuna jalan."""
    try:
        sheet = pygame.image.load(filename).convert_alpha()
        sheet_w, sheet_h = sheet.get_size()
        frame_w = sheet_w // num_frames
        
        frames = []
        for i in range(num_frames):
            rect = pygame.Rect(i * frame_w, 0, frame_w, sheet_h)
            frame_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            frame_surface.blit(sheet, (0, 0), rect)
            scaled_frame = pygame.transform.scale(frame_surface, (width_scale, height_scale))
            frames.append(scaled_frame)
            
        return frames
    except pygame.error as e:
        print(f"Gagal memuat sprite {filename}: {e}")
        fallback = pygame.Surface((width_scale, height_scale), pygame.SRCALPHA)
        pygame.draw.rect(fallback, (255, 0, 255), (0, 0, width_scale, height_scale))
        return [fallback] * num_frames

# --- 1. Load Background ---
try:
    bg_original = pygame.image.load("wallpaper game proglan.png").convert()
    background = pygame.transform.scale(bg_original, (WIDTH, HEIGHT))
except pygame.error as e:
    print(f"Gagal memuat wallpaper: {e}")
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(BLACK)

# --- 2. Load Sprite Animasi Sukuna Jalan ---
sukuna_walk_right = load_spritesheet("gerak sukuna ke kanan.png", 5)
sukuna_walk_left = load_spritesheet("gerak sukuna ke kiri.png", 5)

# --- 3. Load Animasi Fuuga Sukuna (6 Gambar Terpisah) ---
sukuna_fuuga_frames = []
num_fuuga_frames = 6
for i in range(1, num_fuuga_frames + 1):
    file_name = f"fuuga_sukuna_{i}.png"
    try:
        frame_img = pygame.image.load(file_name).convert_alpha()
        bg_color = frame_img.get_at((0, 0)) 
        frame_img.set_colorkey(bg_color)
        
        orig_w, orig_h = frame_img.get_size()
        scale_factor = 90 / orig_h 
        new_w = int(orig_w * scale_factor)
        new_h = 90
        
        scaled_frame = pygame.transform.scale(frame_img, (new_w, new_h))
        sukuna_fuuga_frames.append(scaled_frame)
    except pygame.error as e:
        print(f"Gagal memuat file {file_name}: {e}")
        fallback = pygame.Surface((80, 90), pygame.SRCALPHA)
        sukuna_fuuga_frames.append(fallback)

# --- 4. Load Proyektil Panah Api Fuuga ---
try:
    arrow_img = pygame.image.load("panah fuuga sukuna.png").convert_alpha()
    fuuga_arrow_sprite = pygame.transform.scale(arrow_img, (75, 40))
except pygame.error as e:
    print(f"Gagal memuat panah fuuga: {e}")
    fuuga_arrow_sprite = pygame.Surface((75, 40))
    fuuga_arrow_sprite.fill((255, 69, 0))

# --- 5. BARU: Load Spritesheet Mahoraga (6 Frame) - PERBAIKAN TOTAL ---
mahoraga_frames = []
try:
    # Muat file tunggal yang berjejer ke samping
    m_sheet = pygame.image.load("sprite mahoraga ke kiri.png").convert_alpha()
    
    m_sheet_w, m_sheet_h = m_sheet.get_size()
    # Karena ada 6 gerakan berjejer, lebar total dibagi 6
    m_frame_w = m_sheet_w // 6
    
    # Potong menjadi 6 bagian secara horizontal
    for i in range(6):
        m_rect = pygame.Rect(i * m_frame_w, 0, m_frame_w, m_sheet_h)
        m_surface = pygame.Surface(m_rect.size, pygame.SRCALPHA)
        m_surface.blit(m_sheet, (0, 0), m_rect)
        
        # AMBIL WARNA BACKGROUND DARI AREA AMAN:
        # Kita ambil contoh warna background di koordinat (2, 2) di setiap frame.
        # Ini adalah warna abu-abu kertas latar belakangnya, jadi badan Mahoraga aman ga bakal bolong.
        m_bg_color = m_surface.get_at((2, 2))
        m_surface.set_colorkey(m_bg_color)
        
        # Scaling agar Mahoraga terlihat raksasa (Lebar: 110px, Tinggi: 130px)
        scaled_m = pygame.transform.scale(m_surface, (110, 130))
        mahoraga_frames.append(scaled_m)
        
    print("Berhasil memotong spritesheet Mahoraga dengan aman!")
except Exception as e:
    print(f"Peringatan: Gagal memuat gambar Mahoraga karena ({e}). Menggunakan kotak fallback.")
    dummy = pygame.Surface((110, 130), pygame.SRCALPHA)
    pygame.draw.rect(dummy, (150, 0, 150), (0, 0, 110, 130))
    mahoraga_frames = [dummy] * 6

# --- 6. BARU: Load Spritesheet Ledakan Fuuga (5 Frame) - MEGA EXPANSION ---
explosion_frames = []
try:
    exp_sheet = pygame.image.load("ledakan fuuga sukuna.png").convert_alpha()
    exp_sheet.set_colorkey((255, 255, 255))
    
    exp_sheet_w, exp_sheet_h = exp_sheet.get_size()
    
    if exp_sheet_w > 0 and exp_sheet_h > 0:
        exp_frame_w = exp_sheet_w // 5
        
        for i in range(5):
            exp_rect = pygame.Rect(i * exp_frame_w, 0, exp_frame_w, exp_sheet_h)
            
            if (i * exp_frame_w) + exp_frame_w <= exp_sheet_w:
                exp_surface = pygame.Surface(exp_rect.size, pygame.SRCALPHA)
                exp_surface.blit(exp_sheet, (0, 0), exp_rect)
                
                # JANGAN di-scale dulu di sini, simpan surface aslinya agar resolusinya tajam
                explosion_frames.append(exp_surface)
                
    print("Berhasil memuat animasi dasar ledakan Fuuga!")
except Exception as e:
    print(f"Peringatan: Gagal memuat ledakan karena ({e})")
    # Buat fallback jika gambar bermasalah
    explosion_frames = [pygame.Surface((64, 64), pygame.SRCALPHA)] * 5

# =========================
# GROUND
# =========================
GROUND_Y = 500

# =========================
# PLAYER (SUKUNA)
# =========================
player_w = 60 
player_h = 85
player_x = 100
player_y = GROUND_Y - player_h 

player_speed = 8
player_dir = "right"

# Animasi Jalan
anim_frame = 0
anim_speed = 0.2  
is_moving = False

# Animasi Skill Fuuga
is_casting_fuuga = False
fuuga_anim_frame = 0.0
fuuga_anim_speed = 0.15  

# =========================
# ATTACK SYSTEM
# =========================
attack_mode = 0        
last_attack_mode = 0  
has_shot = False 
projectiles = []
# List penampung ledakan aktif di layar
explosions = []

# ========================================================
# BARU: SYSTEM OBSTACLE (MAHORAGA ONLY) - JEDA DILAMAKAN & ACAK
# ========================================================
obstacles = [] 
last_spawn_time = pygame.time.get_ticks()

# Bikin jeda pertamanya acak antara 3 sampai 5 detik (3000 ms hingga 5000 ms)
spawn_cooldown = random.randint(3000, 5500) 

# Dimensi Hitbox Mahoraga
mahoraga_w = 90
mahoraga_h = 125

def spawn_mahoraga():
    """Fungsi khusus mendatangkan Mahoraga dari kanan layar."""
    obstacles.append({
        "x": WIDTH + random.randint(10, 100),
        "y": GROUND_Y - mahoraga_h,
        "w": mahoraga_w,
        "h": mahoraga_h,
        "vx": -4,                   
        "hp": 3,                    
        "anim_frame": 0.0,          
        "anim_speed": 0.18          
    })

# =========================
# FONT
# =========================
font = pygame.font.SysFont("arial", 50)

# =========================
# GAME LOOP
# =========================
running = True
game_over = False

while running:

    # =========================
    # EVENTS
    # =========================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # =========================
    # GESTURE DETECTION INPUT
    # =========================
    current_time = pygame.time.get_ticks()
    right_finger_count, left_movement, left_is_fist = tracker.update_frame()

    is_moving = False

    # 1. LOGIKA GERAKAN SUKUNA
    if not game_over and left_is_fist and not is_casting_fuuga:
        if left_movement == "left":
            player_x -= player_speed
            player_dir = "left"
            is_moving = True
        elif left_movement == "right":
            player_x += player_speed
            player_dir = "right"
            is_moving = True

    # ========================================================
    # 2. LOGIKA GESTURE - SEKARANG FUUGA PAKE 1 JARI
    # ========================================================
    # Serangan 1 jari (Slash) dihapus. 1 Jari sekarang langsung memicu Fuuga (Mode 2)
    if right_finger_count == 1:
        current_mode = 2  # Langsung set ke mode 2 (Fuuga)
    else:
        current_mode = 0  # Tangan diturunkan atau jumlah jari lain = siaga

    # RE-ARM MECHANISM: Kunci baru terbuka jika tangan kembali siaga (0 jari / tidak 1 jari)
    if current_mode == 0:
        has_shot = False
        attack_mode = 0
    else:
        # Selama jari masih nangkring di atas dan belum pernah nembak
        if not has_shot and not is_casting_fuuga:
            attack_mode = current_mode
        else:
            attack_mode = 0 # Mengunci serangan agar tidak spam walau 1 jari ditahan terus

    # ========================================================
    # 3. EKSEKUSI JURUS SUKUNA (HANYA FUUGA)
    # ========================================================
    if attack_mode == 2 and not game_over:
        if not has_shot:
            if not is_casting_fuuga:
                is_casting_fuuga = True
                fuuga_anim_frame = 0.0
                player_dir = "right"  # Paksa hadap kanan saat merapal Fuuga
                has_shot = True 
                attack_mode = 0  # Langsung kunci mati 

    # =========================
    # UPDATE ANIMATION FUUGA LOGIC (ANTI SPAM DOSEN)
    # =========================
    if is_casting_fuuga and not game_over:
        fuuga_anim_frame += fuuga_anim_speed
        current_frame_idx = int(fuuga_anim_frame)
        
        if current_frame_idx == 4:
            if is_casting_fuuga == True and not any(p["type"] == "fuuga" for p in projectiles):
                projectiles.append({
                    "x": player_x + player_w + 10,
                    "y": player_y + 30,
                    "vx": 16, 
                    "type": "fuuga",       
                    "pierce_count": 1,     
                    "hit_list": []        
                })

        if fuuga_anim_frame >= 6:
            is_casting_fuuga = False
            fuuga_anim_frame = 0.0
            attack_mode = 0  

    # ========================================================
    # BARU: LOGIKA SPAWN MAHORAGA (Dinamis: Setiap 3 Detik Atau Lebih)
    # ========================================================
    if not game_over:
        if current_time - last_spawn_time >= spawn_cooldown:
            spawn_mahoraga()
            last_spawn_time = current_time
            
            # SETELAH SPAWN, ACAK ULANG JEDA BERIKUTNYA!
            # Ini bikin Mahoraga keluar minimal 3 detik (3000ms), bisa juga 4 detik, bahkan 6 detik baru keluar.
            spawn_cooldown = random.randint(3000, 6000)

    # SCREEN LIMIT SUKUNA
    if player_x < 0: player_x = 0
    if player_x > WIDTH - player_w: player_x = WIDTH - player_w

    # UPDATE FRAME ANIMASI JALAN SUKUNA
    if not is_casting_fuuga:
        if is_moving and not game_over:
            anim_frame += anim_speed
            if anim_frame >= 5: anim_frame = 0
        else:
            anim_frame = 0 

    # =========================
    # RENDER & GAME LOGIC DRAW
    # =========================
    screen.blit(background, (0, 0))
    pygame.draw.line(screen, (50, 50, 50), (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

    # Hitbox Sukuna
    player_rect = pygame.Rect(player_x, player_y, player_w, player_h)

    # --- DRAW SUKUNA SPRITE ---
    if is_casting_fuuga:
        current_sprite = sukuna_fuuga_frames[int(fuuga_anim_frame)]
        sprite_rect = current_sprite.get_rect()
        sprite_rect.centerx = player_x + (player_w // 2)
        sprite_rect.bottom = GROUND_Y
        screen.blit(current_sprite, sprite_rect)
    else:
        if player_dir == "right":
            current_sprite = sukuna_walk_right[int(anim_frame)]
        else:
            current_sprite = sukuna_walk_left[int(anim_frame)]
            
        sprite_rect = current_sprite.get_rect()
        sprite_rect.centerx = player_x + (player_w // 2)
        sprite_rect.bottom = GROUND_Y
        screen.blit(current_sprite, sprite_rect)

    # --- LOGIKA & DRAW PELURU ---
    for proj in projectiles[:]:
        if not game_over:
            proj["x"] += proj["vx"]

        if proj["type"] == "slash":
            pygame.draw.line(screen, (138, 43, 226), (int(proj["x"] - 10), int(proj["y"])), (int(proj["x"] + 10), int(proj["y"])), 4)
        elif proj["type"] == "fuuga":
            screen.blit(fuuga_arrow_sprite, (int(proj["x"]), int(proj["y"] - 15)))

        if proj["x"] < 0 or proj["x"] > WIDTH:
            projectiles.remove(proj)


    # ========================================================
    # BARU: UPDATE & DRAW EFEK LEDAKAN FUUGA (MEGA EXPLOSION EFFECT)
    # ========================================================
    for exp in explosions[:]:
        if not game_over:
            exp["anim_frame"] += exp["anim_speed"]
            
        current_idx = int(exp["anim_frame"])
        
        if current_idx < 5:
            base_sprite = explosion_frames[current_idx]
            
            # === RUMUS MATEMATIKA MELEBAR (Eksponensial) ===
            # Frame 0: Ukuran standar (skala 1.0)
            # Frame 4 (Terakhir): Ukuran raksasa (skala berkembang pesat sampai mendominasi layar)
            # Kita gunakan current_idx untuk menentukan faktor pengali ukuran
            skala_faktor = 1.0 + (current_idx * 0.45) # Mengembang 65% lebih besar di setiap frame!
            
            # Kalkulasi dimensi baru berdasarkan skala_faktor
            orig_w, orig_h = base_sprite.get_size()
            new_w = int(orig_w * skala_faktor * 1.5) # Dikali 1.5 sebagai ukuran dasar kemegahan
            new_h = int(orig_h * skala_faktor * 1.5)
            
            # Lakukan transformasi scale secara real-time berdasarkan frame aktif
            mega_exp_sprite = pygame.transform.scale(base_sprite, (new_w, new_h))
            
            # TRICK KORREKSI POSISI (Anchor Center):
            # Biar ledakannya mengembang dari TITIK TENGAH (bukan melar ke kanan bawah doang),
            # kita geser koordinat X dan Y mundur setengah dari pertambahan ukurannya.
            render_x = exp["x"] - (new_w // 2)
            render_y = exp["y"] - (new_h // 2)
            
            # Gambar ledakan megah ke layar
            screen.blit(mega_exp_sprite, (render_x, render_y))
        else:
            # Selesai 5 frame, hapus dari memori
            explosions.remove(exp)


    # =========================
    # BARU: LOGIKA UPDATE & DRAW MAHORAGA
    # =========================
    for obs in obstacles[:]:
        if not game_over:
            obs["x"] += obs["vx"]
            # Jalankan siklus animasi lari Mahoraga (looping 6 frame)
            obs["anim_frame"] += obs["anim_speed"]
            if obs["anim_frame"] >= 6:
                obs["anim_frame"] = 0

        # Hitbox persegi Mahoraga untuk kalkulasi colliderect
        mahoraga_rect = pygame.Rect(obs["x"], obs["y"], obs["w"], obs["h"])
        
        # --- DRAW SPRITE MAHORAGA ---
        m_current_sprite = mahoraga_frames[int(obs["anim_frame"])]
        m_sprite_rect = m_current_sprite.get_rect()
        m_sprite_rect.x = obs["x"]
        m_sprite_rect.y = obs["y"]
        screen.blit(m_current_sprite, m_sprite_rect)

        # Draw Teks HP di atas Kepala Mahoraga
        if not game_over:
            hp_font = pygame.font.SysFont("arial", 22)
            hp_text = hp_font.render(f"HP: {obs['hp']}", True, (255, 69, 0))
            screen.blit(hp_text, (obs["x"] + obs["w"]//2 - hp_text.get_width()//2, obs["y"] - 25))

        # Hapus Mahoraga dari list jika lolos sampai ujung kiri layar
        if obs["x"] < -150:
            obstacles.remove(obs)

        # Cek Tabrakan Sukuna vs Mahoraga
        if player_rect.colliderect(mahoraga_rect):
            game_over = True

        # ========================================================
        # PERBAIKAN: Cek Tabrakan Peluru Sukuna vs Mahoraga (Fuuga 1 Kali Hit)
        # ========================================================
        for proj in projectiles[:]:
            if proj["type"] == "slash":
                proj_rect = pygame.Rect(proj["x"] - 10, proj["y"] - 2, 20, 4)
            else:
                # Hitbox Panah Fuuga
                proj_rect = pygame.Rect(proj["x"], proj["y"] - 15, 75, 40)

            # Jika peluru mengenai Mahoraga
            if mahoraga_rect.colliderect(proj_rect):
                obs_id = id(obs) 
                if obs_id not in proj["hit_list"]:
                    proj["hit_list"].append(obs_id)

                    # MEKANIK JURUS FUUGA (Hanya Bisa Membunuh 1 Mahoraga)
                    if proj["type"] == "fuuga":
                        obs["hp"] = 0  # Mahoraga langsung mati
                        
                        # BARU: Daftarkan ledakan baru di koordinat Mahoraga saat ini
                        explosions.append({
                            "x": obs["x"] - 15,          # Geser sedikit ke kiri agar sentral ledakannya pas
                            "y": obs["y"] + 5,           # Sejajar tinggi badan Mahoraga
                            "anim_frame": 0.0,           # Mulai dari frame index ke-0
                            "anim_speed": 0.25           # Kecepatan animasi ledakan (sekitar 4 frame game loop per frame sprite)
                        })
                        
                        # Langsung lenyapkan panah Fuuga dari layar
                        if proj in projectiles:
                            projectiles.remove(proj)
                            
                    # MEKANIK JURUS SLASH (Mencicil HP)
                    elif proj["type"] == "slash":
                        obs["hp"] -= 1 
                        proj["tierce_count"] -= 1
                        if proj["tierce_count"] <= 0:
                            if proj in projectiles: 
                                projectiles.remove(proj)

                    # Jika HP Mahoraga Habis, langsung lenyap dari layar
                    if obs["hp"] <= 0:
                        if obs in obstacles:
                            obstacles.remove(obs)
                            break # Keluar dari loop peluru untuk objek Mahoraga ini karena sudah mati

    # Game Over Screen
    if game_over:
        text = font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100))

    pygame.display.flip()
    clock.tick(60)

# ========================================================
# EXIT PROCESS
# ========================================================
print("Menutup kamera dan melepaskan resource...")
tracker.release()  
pygame.quit()
sys.exit()