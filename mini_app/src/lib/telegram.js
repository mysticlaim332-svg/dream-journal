/**
 * Telegram WebApp helpers.
 * window.Telegram.WebApp is injected by the Telegram SDK script.
 */

export const tg = window.Telegram?.WebApp ?? null

function getWebApp() {
  return window.Telegram?.WebApp ?? tg
}

/** Call once at app startup */
export function initTelegram() {
  const webApp = getWebApp()
  if (!webApp) return
  webApp.ready()
  webApp.expand()
  webApp.setHeaderColor('#0B0C1E')
  webApp.setBackgroundColor('#0B0C1E')
}

/** Telegram user from initData */
export function getTelegramUser() {
  return getWebApp()?.initDataUnsafe?.user ?? null
}

/** Raw initData string — sent to our API for validation */
export function getInitData() {
  return getWebApp()?.initData ?? ''
}

/** Show or hide Telegram's native Back button */
export function useBackButton(onBack) {
  if (!tg) return
  tg.BackButton.show()
  tg.BackButton.onClick(onBack)
  return () => {
    tg.BackButton.offClick(onBack)
    tg.BackButton.hide()
  }
}

/** Haptic feedback */
export const haptic = {
  light: () => tg?.HapticFeedback?.impactOccurred('light'),
  medium: () => tg?.HapticFeedback?.impactOccurred('medium'),
  success: () => tg?.HapticFeedback?.notificationOccurred('success'),
  error: () => tg?.HapticFeedback?.notificationOccurred('error'),
}
