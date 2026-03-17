# Changelog

Alle merkbare endringer i dette prosjektet dokumenteres i denne filen.

## 1.1.1 - 2026-03-17

### Fixed
- Fikset feil der `Sist oppdatert`-sensor kunne kaste `AttributeError` når `last_update_success_time` manglet på coordinator.
- Lagt til robust fallback i sensoren ved manglende coordinator-attributt.
- Oppdaterte coordinator til å sette tidspunkt for siste vellykkede oppdatering.
