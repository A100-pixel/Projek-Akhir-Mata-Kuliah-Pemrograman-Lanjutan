import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        # PERBAIKAN UTAMA: Hapus cv2.CAP_DSHOW agar tidak dipaksa jika driver crash.
        # Jika indeks 0 tetap hitam, nanti coba ganti ke indeks 1 atau 2.
        self.cap = cv2.VideoCapture(0) 
        
        # Pengaman jika kamera benar-benar tidak terbuka
        if not self.cap.isOpened():
            print("PENGINGAT: Kamera utama (indeks 0) tidak terdeteksi, mencoba indeks alternatif...")
            self.cap = cv2.VideoCapture(1)

        self.screen_center_x = None

    def update_frame(self):
        """
        Fungsi utama untuk membaca kamera, memproses tangan kiri & kanan.
        """
        if not self.cap.isOpened():
            return 0, "idle", False

        success, frame = self.cap.read()
        if not success:
            # Jika sesekali gagal baca frame, return status aman biar Pygame gak freeze
            return 0, "idle", False

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        self.screen_center_x = w // 2

        cv2.line(frame, (self.screen_center_x, 0), (self.screen_center_x, h), (255, 0, 0), 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        right_finger_count = 0
        left_movement = "idle"
        left_is_fist = False

        if results.multi_hand_landmarks and results.multi_handedness:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                hand_label = results.multi_handedness[idx].classification[0].label
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                lm = hand_landmarks.landmark

                # ==========================================
                # TANGAN KANAN: HITUNG JARI (SERANGAN)
                # ==========================================
                if hand_label == "Right":
                    if lm[8].y < lm[6].y: right_finger_count += 1    # Telunjuk
                    if lm[12].y < lm[10].y: right_finger_count += 1  # Tengah
                    if lm[16].y < lm[14].y: right_finger_count += 1  # Manis
                    if lm[20].y < lm[18].y: right_finger_count += 1  # Kelingking

                # ==========================================
                # TANGAN KIRI: KONTROL WRIST & KEPAL (PERGERAKAN)
                # ==========================================
                elif hand_label == "Left":
                    fingers_open = 0
                    if lm[8].y < lm[6].y: fingers_open += 1
                    if lm[12].y < lm[10].y: fingers_open += 1
                    if lm[16].y < lm[14].y: fingers_open += 1
                    if lm[20].y < lm[18].y: fingers_open += 1
                    
                    if fingers_open == 0:
                        left_is_fist = True

                    wrist_x = int(lm[0].x * w)
                    
                    if wrist_x < self.screen_center_x - 40:
                        left_movement = "left"
                    elif wrist_x > self.screen_center_x + 40:
                        left_movement = "right"
                    else:
                        left_movement = "idle"

        # Tampilkan status di layar kamera
        cv2.putText(frame, f"Right Jari: {right_finger_count}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Left Move: {left_movement} | Fist: {left_is_fist}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow("Hand Tracking", frame)
        
        # PERBAIKAN: Mask bit cv2.waitKey agar kompatibel dengan beberapa versi sistem OS
        if cv2.waitKey(1) & 0xFF == ord('q'):
            pass

        return right_finger_count, left_movement, left_is_fist

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()