"""Refresh verified marketing copy from the apps' existing translations.

The website build uses content/apps.json; app repositories are only needed
when deliberately refreshing this source snapshot.
"""
from pathlib import Path
import json
import re
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('C:/dev/projects/flutter')

def clean(value):
    value = re.sub(r'[—–]+', '. ', value)
    value = re.sub(r'[🎈🎤🎮🚀✨😉]', '', value)
    return re.sub(r'\s+', ' ', value).strip()

definitions = {
    'booktou': dict(name='Booktou', category='reading', accent='#4f46a8', tint='#f0edfb', icon='assets/booktou/marketing/icon.webp', apple='6795242771', title='onboardingWelcomeTitle', summary='appDescription', features=[('onboardingWelcomeTitle','onboardingWelcomeBody'),('onboardingTrackTitle','onboardingTrackBody'),('onboardingFocusTitle','onboardingFocusBody'),('pomodoroTimerFeature','pomodoroDescription')], images=['assets/booktou/marketing/track-books.webp','assets/booktou/marketing/statistics.webp','assets/booktou/marketing/notes-quotes.webp']),
    'speaktou': dict(name='Speaktou', category='speaking', accent='#087e73', tint='#e9f5f1', icon='assets/speaktou/marketing/icon.webp', apple=None, title='practice', summary='onboardingSpeakingDescription', features=[('practice','onboardingSpeakingDescription'),('shareWordCardSubtitle','wordRemindersDescription'),('premiumStatsTitle','premiumStatsDescription'),('yourWordTower','wordTowerEmptyDescription'),('playbackSettings','playbackNoVoices'),('practiceCalendar','progressAccuracyHelp')], images=['assets/speaktou/marketing/practice.webp','assets/speaktou/marketing/word-tower.webp','assets/speaktou/marketing/listening.webp']),
    'notero': dict(name='Notero', category='notes', accent='#9b4d12', tint='#fff3e4', icon='assets/notero-logo.png', apple=None, title='createNotes', summary='onboardingWelcome', features=[('organizeFolders','featureOrganizeFoldersDescription'),('share_notes_on_web','webShareLocalOnlyRule'),('convertToPdf',None),('backup_import','backup_import_description'),('secureNotes','add_password_description')]),
    'lessonta': dict(name='Lessonta', category='study', accent='#235fae', tint='#edf3fd', icon='assets/lessonta/lessonta_logo.png', apple=None, title='lessonSchedule', summary='aboutPageDescription', features=[('lessonSchedule','weeklyLessonDescription'),('attendance','attendanceTracking'),('homeworkReminders','homeworkRemindersDescription'),('examReminders','examRemindersDescription'),('adFreePdfExport','adFreePdfExportDescription'),('lessonReminderNotifications','lessonReminderNotificationsDescription')]),
    'doitly': dict(name='Doitly', category='tasks', accent='#35614c', tint='#eaf4ed', icon='assets/doitly/doitly_logo.png', apple=None, title='appdescription', summary='appdescription', features=[('subtasks',None),('filterByCategory',None),('calendar',None),('statistics','viewYourTaskStatistics'),('backupData','exportYourData'),('security','askPinOnAppOpen')]),
    'dictiony': dict(name='Dictiony', category='diction', accent='#925032', tint='#fcf0e9', icon='assets/dictiony/dictiony_logo.png', apple=None, title='onboardingWelcomeSubtitle', summary='appDescription', features=[('onboardingFeatureTextReading','onboardingFeatureTextReadingDesc'),('onboardingFeatureExercises','onboardingFeatureExercisesDesc'),('onboardingFeatureGames','onboardingFeatureGamesDesc')]),
    'beanjup': dict(name='Beanjup', category='arcade', accent='#236f68', tint='#e4f4f1', icon='assets/beanjup-logo.png', apple='6792344729'),
    'wordballoonpop': dict(name='Word Balloon Pop', category='voicegame', accent='#7a42a6', tint='#f4ecfb', icon='assets/wordballoonpop/word_balloon_pop_logo.png', apple=None, title='onboardingVoiceTitle', summary='onboardingWelcomeDesc', features=[('onboardingVoiceTitle','onboardingVoiceDesc'),('onboardingModesTitle','onboardingModesDesc')]),
}

overrides = {
    'booktou': {
        'en': ('A home for your reading life.', 'Keep your personal library, reading sessions and favourite passages together. Track the books you are reading, save notes and quotes, build a reading habit and see your progress over time.'),
        'tr': ('Okuma hayatının kendi köşesi.', 'Kişisel kütüphaneni, okuma seanslarını ve sevdiğin satırları bir arada tut. Okuduğun kitapları takip et, not ve alıntılarını kaydet, okuma alışkanlığı kazan ve zaman içindeki ilerlemeni gör.'),
    },
    'dictiony': {
        'en': ('Find your speaking rhythm.', 'Practise reading aloud with categorised texts, diction exercises and games. Listen to reference speech, work through a personal programme and follow your practice history. A speaking practice tool, not a medical assessment.'),
        'tr': ('Konuşmanın ritmini bul.', 'Kategorilere ayrılmış metinler, diksiyon egzersizleri ve oyunlarla sesli okuma pratiği yap. Örnek okumaları dinle, kişisel programını takip et ve çalışma geçmişini gör. Tıbbi değerlendirme değil, konuşma pratiği aracıdır.'),
    },
    'doitly': {
        'en': ('A little order. A lighter day.', 'Keep everyday tasks in a simple list. Break bigger jobs into subtasks, organise them by category and see dated tasks on your calendar. Review completion statistics, protect access with a PIN and keep a backup of your data.'),
        'tr': ('Biraz düzen. Daha rahat bir gün.', 'Günlük işlerini sade bir listede tut. Büyük işleri alt görevlere ayır, kategorilerle düzenle ve tarihli görevlerini takvimde gör. Tamamlama istatistiklerine bak, PIN ile erişimi koru ve verilerini yedekle.'),
    },
    'lessonta': {
        'en': ('Your school week, together.', 'Keep your lesson timetable, attendance, homework and exams in one place. Set reminders, follow attendance by lesson and export schedules or records as PDF. Built for organising your own student life.'),
        'tr': ('Okul haftan, bir arada.', 'Ders programını, devamsızlığını, ödevlerini ve sınavlarını tek yerde tut. Hatırlatıcılar ayarla, ders bazında devamsızlığını takip et ve programını veya kayıtlarını PDF olarak dışa aktar. Kendi öğrencilik hayatını düzenlemek için.'),
    },
    'notero': {
        'en': ('Give your thoughts a place.', 'Write and organise notes in folders, keep them on your device and export them as PDF. With local network sharing, open and edit your notes in a browser on another device on the same network. Back up your notes and protect app access with a password.'),
        'tr': ('Düşüncelerine bir yer aç.', 'Notlarını yaz, klasörlerle düzenle, cihazında sakla ve PDF olarak dışa aktar. Yerel ağ paylaşımıyla aynı ağa bağlı başka bir cihazın tarayıcısından notlarını açıp düzenle. Notlarını yedekle ve uygulama erişimini şifreyle koru.'),
    },
    'wordballoonpop': {
        'en': ('Say the word. Pop the balloon.', 'Use your voice to pop word balloons. Practise speaking through classic levels, endless rounds and survival mode, with coins and power-ups along the way. Microphone access and a compatible speech recogniser are needed.'),
        'tr': ('Kelimeyi söyle. Balonu patlat.', 'Kelime balonlarını sesinle patlat. Klasik seviyeler, sonsuz turlar ve hayatta kalma modunda konuşarak oyna; yol boyunca para ve güçlendirmeler topla. Mikrofon erişimi ve uyumlu bir konuşma tanıyıcı gerekir.'),
    },
}

speaktou = {
    'en': ('Speak a little. Every day.', 'Practise speaking English, Spanish, French or German with short daily cards. Listen, read aloud and review the words that matched. Build a streak, collect daily vocabulary and follow your progress. Premium adds practice beyond your daily goal and focused word review.'),
    'tr': ('Her gün biraz konuş.', 'Kısa günlük kartlarla İngilizce, İspanyolca, Fransızca veya Almanca konuşma pratiği yap. Dinle, sesli oku ve eşleşen kelimeleri incele. Serini oluştur, günlük kelimeleri biriktir ve ilerlemeni takip et. Premium ile günlük hedefinden sonra da pratik yapabilir, kelime tekrarı çalışabilirsin.'),
    'de': ('Jeden Tag ein bisschen sprechen.', 'Übe Englisch, Spanisch, Französisch oder Deutsch mit kurzen täglichen Karten. Höre zu, lies laut und überprüfe erkannte Wörter. Sammle tägliche Vokabeln und verfolge deinen Fortschritt. Premium bietet zusätzliche Übungen nach deinem Tagesziel und gezielte Wortwiederholung.'),
    'es': ('Habla un poco cada día.', 'Practica inglés, español, francés o alemán con tarjetas diarias breves. Escucha, lee en voz alta y revisa las palabras reconocidas. Aprende vocabulario diario y sigue tu progreso. Premium permite continuar después de tu objetivo diario y repasar palabras.'),
    'fr': ('Un peu de pratique chaque jour.', 'Pratiquez l’anglais, l’espagnol, le français ou l’allemand avec de courtes cartes quotidiennes. Écoutez, lisez à voix haute et vérifiez les mots reconnus. Enrichissez votre vocabulaire et suivez vos progrès. Premium permet de continuer après votre objectif quotidien et de réviser les mots.'),
    'it': ('Parla un po’ ogni giorno.', 'Esercitati in inglese, spagnolo, francese o tedesco con brevi schede quotidiane. Ascolta, leggi ad alta voce e controlla le parole riconosciute. Impara vocaboli e segui i tuoi progressi. Premium permette di continuare oltre l’obiettivo giornaliero e ripassare le parole.'),
    'pt': ('Fale um pouco todos os dias.', 'Pratique inglês, espanhol, francês ou alemão com cartões diários curtos. Ouça, leia em voz alta e reveja as palavras reconhecidas. Aprenda vocabulário e acompanhe o seu progresso. Premium permite continuar após a meta diária e revisar palavras.'),
    'ar': ('تحدث قليلاً كل يوم.', 'تدرّب على الإنجليزية أو الإسبانية أو الفرنسية أو الألمانية ببطاقات يومية قصيرة. استمع واقرأ بصوت عالٍ وراجع الكلمات التي تم التعرف عليها. تعلّم مفردات يومية وتابع تقدمك. يتيح Premium مواصلة التدريب بعد هدفك اليومي ومراجعة الكلمات.'),
    'ru': ('Говорите понемногу каждый день.', 'Практикуйте английский, испанский, французский или немецкий с короткими ежедневными карточками. Слушайте, читайте вслух и проверяйте распознанные слова. Изучайте лексику и следите за прогрессом. Premium позволяет продолжить после дневной цели и повторять слова.'),
    'pl': ('Mów trochę każdego dnia.', 'Ćwicz angielski, hiszpański, francuski lub niemiecki z krótkimi codziennymi kartami. Słuchaj, czytaj na głos i sprawdzaj rozpoznane słowa. Poznawaj słownictwo i śledź postępy. Premium pozwala ćwiczyć po osiągnięciu dziennego celu i powtarzać słowa.'),
    'hi': ('हर दिन थोड़ा बोलें।', 'छोटे दैनिक कार्डों से अंग्रेज़ी, स्पेनिश, फ़्रेंच या जर्मन बोलने का अभ्यास करें। सुनें, ज़ोर से पढ़ें और पहचाने गए शब्द देखें। रोज़ नई शब्दावली सीखें और प्रगति देखें। Premium से दैनिक लक्ष्य के बाद भी अभ्यास और शब्दों की समीक्षा कर सकते हैं।'),
    'id': ('Berbicara sedikit setiap hari.', 'Latih bahasa Inggris, Spanyol, Prancis atau Jerman dengan kartu harian singkat. Dengarkan, baca dengan suara keras dan periksa kata yang dikenali. Pelajari kosakata dan pantau kemajuan. Premium memungkinkan latihan setelah target harian dan pengulangan kata.'),
    'ja': ('毎日、少しずつ話そう。', '短い毎日のカードで英語、スペイン語、フランス語、ドイツ語の会話を練習できます。音声を聞いて音読し、認識された単語を確認。語彙を増やし、進歩を記録しましょう。Premiumでは毎日の目標達成後も練習を続け、単語を復習できます。'),
    'ko': ('매일 조금씩 말해 보세요.', '짧은 일일 카드로 영어, 스페인어, 프랑스어 또는 독일어 말하기를 연습하세요. 듣고 소리 내어 읽으며 인식된 단어를 확인하세요. 어휘를 배우고 진행 상황을 살펴보세요. Premium으로 일일 목표 달성 후에도 연습하고 단어를 복습할 수 있습니다.'),
    'th': ('ฝึกพูดวันละนิดทุกวัน', 'ฝึกพูดภาษาอังกฤษ สเปน ฝรั่งเศส หรือเยอรมันด้วยการ์ดสั้น ๆ ทุกวัน ฟัง อ่านออกเสียง และตรวจคำที่ระบบจดจำ เรียนรู้คำศัพท์และติดตามความก้าวหน้า Premium ช่วยให้ฝึกต่อหลังบรรลุเป้าหมายประจำวันและทบทวนคำศัพท์ได้'),
    'vi': ('Nói một chút mỗi ngày.', 'Luyện nói tiếng Anh, Tây Ban Nha, Pháp hoặc Đức với thẻ ngắn hằng ngày. Nghe, đọc thành tiếng và xem các từ được nhận dạng. Học từ vựng và theo dõi tiến bộ. Premium cho phép luyện tiếp sau mục tiêu hằng ngày và ôn từ.'),
    'zh': ('每天开口说一点。', '通过简短的每日卡片练习英语、西班牙语、法语或德语。先听，再朗读，并查看识别出的单词。积累每日词汇，记录学习进展。Premium 可让你在完成每日目标后继续练习，并专项复习单词。'),
}

voice_copy = {
 'en':'Adjust reading speed. Premium lets you choose from the voices available on your device.',
 'tr':'Okuma hızını ayarla. Premium ile cihazındaki kullanılabilir sesler arasından seçim yap.',
 'de':'Passe die Lesegeschwindigkeit an. Mit Premium kannst du aus den auf deinem Gerät verfügbaren Stimmen wählen.',
 'es':'Ajusta la velocidad de lectura. Premium permite elegir entre las voces disponibles en tu dispositivo.',
 'fr':'Réglez la vitesse de lecture. Premium permet de choisir parmi les voix disponibles sur votre appareil.',
 'it':'Regola la velocità di lettura. Premium permette di scegliere tra le voci disponibili sul tuo dispositivo.',
 'pt':'Ajuste a velocidade de leitura. Premium permite escolher entre as vozes disponíveis no seu dispositivo.',
 'ar':'اضبط سرعة القراءة. يتيح Premium الاختيار من الأصوات المتوفرة على جهازك.',
 'ru':'Настройте скорость чтения. Premium позволяет выбирать голоса, доступные на вашем устройстве.',
 'pl':'Dostosuj szybkość czytania. Premium pozwala wybrać głos spośród dostępnych na urządzeniu.',
 'hi':'पढ़ने की गति बदलें। Premium से अपने डिवाइस पर उपलब्ध आवाज़ों में से चुनें।',
 'id':'Atur kecepatan membaca. Premium memungkinkan pilihan suara yang tersedia di perangkat Anda.',
 'ja':'読み上げ速度を調整できます。Premiumでは、お使いの端末で利用できる音声を選べます。',
 'ko':'읽기 속도를 조절하세요. Premium으로 기기에서 사용 가능한 음성을 선택할 수 있습니다.',
 'th':'ปรับความเร็วในการอ่าน Premium ให้คุณเลือกเสียงที่มีอยู่ในอุปกรณ์ได้',
 'vi':'Điều chỉnh tốc độ đọc. Premium cho phép chọn giọng có sẵn trên thiết bị của bạn.',
 'zh':'调整朗读速度。Premium 可让你选择设备上可用的声音。',
}

bean = {
 'en': ['One tap. One more jump.', 'Time your jump, pass through the gap and keep climbing. Chase your high score in Classic mode or take on 100 Adventure levels across 10 regions.', 'One-tap play', 'The bean moves automatically. Tap at the right moment to jump.', 'Classic mode', 'Climb as high as you can and beat your personal best.', 'Adventure', '100 levels across 10 regions, with changing challenges and boss stages.'],
 'tr': ['Bir dokunuş. Bir zıplayış daha.', 'Zıplayışını zamanla, aralıktan geç ve yükselmeye devam et. Klasik modda rekorunu kovala veya 10 bölgede 100 Macera seviyesini tamamla.', 'Tek dokunuşla oyun', 'Fasulye kendi hareket eder. Zıplamak için doğru anda dokun.', 'Klasik mod', 'Çıkabildiğin kadar yükseğe çık ve kendi rekorunu kır.', 'Macera', '10 bölgede 100 seviye, değişen zorluklar ve bölüm sonu aşamaları.'],
 'de': ['Ein Tippen. Noch ein Sprung.', 'Springe im richtigen Moment durch die Lücke und klettere weiter. Jage deinen Highscore im Classic-Modus oder spiele 100 Adventure-Level in 10 Regionen.', 'Mit einem Tippen', 'Die Bohne bewegt sich automatisch. Tippe im richtigen Moment zum Springen.', 'Classic-Modus', 'Klettere so hoch wie möglich und übertriff deinen Rekord.', 'Adventure', '100 Level in 10 Regionen mit wechselnden Herausforderungen und Boss-Leveln.'],
 'fr': ['Un geste. Un saut de plus.', 'Sautez au bon moment, passez dans l’ouverture et continuez à grimper. Battez votre record en mode Classic ou jouez 100 niveaux Adventure dans 10 régions.', 'Une seule touche', 'Le haricot se déplace automatiquement. Touchez au bon moment pour sauter.', 'Mode Classic', 'Grimpez le plus haut possible et battez votre record.', 'Adventure', '100 niveaux dans 10 régions, avec des défis variés et des boss.'],
 'es': ['Un toque. Un salto más.', 'Salta en el momento justo, atraviesa el hueco y sigue subiendo. Supera tu récord en Classic o juega 100 niveles Adventure en 10 regiones.', 'Un solo toque', 'La judía se mueve sola. Toca en el momento adecuado para saltar.', 'Modo Classic', 'Sube lo más alto posible y supera tu récord.', 'Adventure', '100 niveles en 10 regiones con retos variados y fases de jefe.'],
 'pt': ['Um toque. Mais um salto.', 'Salte no momento certo, passe pela abertura e continue a subir. Supere o seu recorde no Classic ou jogue 100 níveis Adventure em 10 regiões.', 'Um único toque', 'O feijão move-se sozinho. Toque no momento certo para saltar.', 'Modo Classic', 'Suba o mais alto possível e supere o seu recorde.', 'Adventure', '100 níveis em 10 regiões com desafios variados e fases de chefe.'],
 'it': ['Un tocco. Un altro salto.', 'Salta al momento giusto, attraversa il varco e continua a salire. Batti il tuo record in Classic o affronta 100 livelli Adventure in 10 regioni.', 'Un solo tocco', 'Il fagiolo si muove da solo. Tocca al momento giusto per saltare.', 'Modalità Classic', 'Sali più in alto che puoi e batti il tuo record.', 'Adventure', '100 livelli in 10 regioni, con sfide diverse e livelli boss.'],
 'id': ['Satu ketukan. Satu lompatan lagi.', 'Lompat pada saat yang tepat, lewati celah dan terus naik. Kejar rekor di Classic atau mainkan 100 level Adventure di 10 wilayah.', 'Satu ketukan', 'Kacang bergerak otomatis. Ketuk pada saat yang tepat untuk melompat.', 'Mode Classic', 'Naik setinggi mungkin dan kalahkan rekor pribadi.', 'Adventure', '100 level di 10 wilayah dengan tantangan beragam dan level bos.'],
}

apps = []
for app_id, definition in definitions.items():
    app = {k:v for k,v in definition.items() if k not in ('title','summary','features')}
    app['id'] = app_id
    icon=Image.open(ROOT/app['icon']).convert('RGBA')
    icon.thumbnail((192,192))
    icon_path=ROOT/'assets'/app_id/'icon.webp'
    icon_path.parent.mkdir(parents=True,exist_ok=True)
    icon.save(icon_path,'WEBP',quality=90,method=6)
    app['icon']=icon_path.relative_to(ROOT).as_posix()
    app['play'] = None if app_id == 'speaktou' else f'https://play.google.com/store/apps/details?id=com.rapheldorsoftware.{app_id}'
    app['apple'] = f'https://apps.apple.com/app/id{app["apple"]}' if app['apple'] else None
    app['images'] = app.get('images') or [q.as_posix() for q in sorted((ROOT/'assets'/app_id/'screens').glob('*.webp'))]
    app['images'] = [p.replace(ROOT.as_posix()+'/', '') for p in app['images']]
    app['imageSizes']={p:list(Image.open(ROOT/p).size) for p in app['images']}
    app['locales'] = {}
    if app_id == 'beanjup':
        for lang, values in bean.items():
            app['locales'][lang] = dict(title=values[0],summary=values[1],features=[{'title':values[i],'body':values[i+1]} for i in (2,4,6)])
    else:
        arbs = sorted((PROJECTS/app_id).glob('lib/**/app_*.arb'))
        for arb in arbs:
            lang = arb.stem.removeprefix('app_')
            data = json.loads(arb.read_text(encoding='utf-8'))
            keys = [definition['title'],definition['summary']]+[k for pair in definition['features'] for k in pair if k]
            missing = [k for k in keys if not isinstance(data.get(k),str)]
            if missing: raise ValueError(f'{app_id}/{lang}: missing {missing}')
            title,summary = data[definition['title']],data[definition['summary']]
            if lang in overrides.get(app_id,{}): title,summary=overrides[app_id][lang]
            if app_id=='speaktou': title,summary=speaktou[lang]
            features=[dict(title=clean(data[t]),body=clean(data[b]) if b else '') for t,b in definition['features']]
            if app_id=='speaktou':
                features=[f for i,f in enumerate(features) if i in (0,1,2,4)]
                features[-1]['body'] = voice_copy[lang]
            if app_id=='notero' and lang=='ro': features[3]['title']='Copie de siguranță și import'
            app['locales'][lang]=dict(title=clean(title),summary=clean(summary),features=features)
    apps.append(app)

(ROOT/'content/apps.json').write_text(json.dumps(apps,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Imported',len(apps),'apps and',sum(len(a['locales']) for a in apps),'localized product pages')
