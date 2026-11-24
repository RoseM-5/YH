export type Locale = 'zh' | 'en' | 'fr' | 'es' | 'ar';

const language = document.documentElement.lang;
export const locale: Locale = language === 'en' || language === 'fr' || language === 'es' || language === 'ar'
  ? language
  : 'zh';

export const ui = {
  zh: { openMenu: '打开菜单', closeMenu: '关闭菜单', muteVideo: '静音视频', enableSound: '开启视频声音', mute: '静音', soundOn: '开启声音', playVideo: '播放视频', pauseVideo: '暂停视频' },
  en: { openMenu: 'Open menu', closeMenu: 'Close menu', muteVideo: 'Mute video', enableSound: 'Turn on video sound', mute: 'Mute', soundOn: 'Sound on', playVideo: 'Play video', pauseVideo: 'Pause video' },
  fr: { openMenu: 'Ouvrir le menu', closeMenu: 'Fermer le menu', muteVideo: 'Couper le son de la vidéo', enableSound: 'Activer le son de la vidéo', mute: 'Couper le son', soundOn: 'Son activé', playVideo: 'Lire la vidéo', pauseVideo: 'Mettre la vidéo en pause' },
  es: { openMenu: 'Abrir menú', closeMenu: 'Cerrar menú', muteVideo: 'Silenciar el vídeo', enableSound: 'Activar el sonido del vídeo', mute: 'Silenciar', soundOn: 'Sonido activado', playVideo: 'Reproducir vídeo', pauseVideo: 'Pausar vídeo' },
  ar: { openMenu: 'فتح القائمة', closeMenu: 'إغلاق القائمة', muteVideo: 'كتم صوت الفيديو', enableSound: 'تشغيل صوت الفيديو', mute: 'كتم الصوت', soundOn: 'الصوت مفعّل', playVideo: 'تشغيل الفيديو', pauseVideo: 'إيقاف الفيديو مؤقتًا' },
}[locale];

export const solutionStatus = (current: number, total: number) => ({
  zh: `第 ${current} 个方案，共 ${total} 个`,
  en: `Solution ${current} of ${total}`,
  fr: `Solution ${current} sur ${total}`,
  es: `Solución ${current} de ${total}`,
  ar: `الحل ${current} من ${total}`,
})[locale];

export const updatesStatus = (start: number, count: number, total: number) => ({
  zh: `展示第 ${start} 项起的 ${count} 条动态，共 ${total} 条`,
  en: `Showing ${count} updates from item ${start} of ${total}`,
  fr: `Affichage de ${count} actualités à partir de l’élément ${start} sur ${total}`,
  es: `Mostrando ${count} novedades desde el elemento ${start} de ${total}`,
  ar: `عرض ${count} تحديثات بدءًا من العنصر ${start} من أصل ${total}`,
})[locale];
