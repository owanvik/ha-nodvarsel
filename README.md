# Nødvarsel for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License](https://img.shields.io/github/license/owanvik/ha-nodvarsel)](LICENSE)

Custom integration for Home Assistant som overvåker aktive nødvarsler fra [nødvarsel.no](https://www.nodvarsel.no).

> **Data levert av [nødvarsel.no](https://www.nodvarsel.no)** – en tjeneste fra DSB, Politiet og Sivilforsvaret.

## Funksjoner

- **Binary sensor** – `on`/`off` basert på om det finnes aktive nødvarsler
- **Antall-sensor** – Viser antall aktive varsler
- **Siste varsel-sensor** – Tittel og detaljer for siste nødvarsel
- **Sist oppdatert-sensor** – Tidspunkt for siste vellykkede sjekk
- **Konfigurerbart oppdateringsintervall** – 30 til 600 sekunder (standard 90)
- **Config flow** – Oppsett via Home Assistant UI

## Installasjon

### HACS (anbefalt)

1. Åpne HACS i Home Assistant
2. Klikk menyen (⋮) → **Egendefinerte repoer**
3. Legg til: `https://github.com/owanvik/ha-nodvarsel` som **Integrasjon**
4. Søk etter "Nødvarsel" og installer
5. Start Home Assistant på nytt
6. Gå til **Innstillinger → Enheter og tjenester → Legg til integrasjon** → søk "Nødvarsel"

### Manuell installasjon

1. Kopier mappen `custom_components/nodvarsel/` til din Home Assistant `config/custom_components/`-mappe
2. Start Home Assistant på nytt
3. Gå til **Innstillinger → Enheter og tjenester → Legg til integrasjon** → søk "Nødvarsel"

## Entiteter

| Entitet | Type | Beskrivelse |
|---|---|---|
| Aktivt nødvarsel | Binary sensor | `on` når det finnes aktive nødvarsler |
| Antall nødvarsler | Sensor | Antall aktive varsler |
| Siste nødvarsel | Sensor | Tittel på siste aktive varsel |
| Sist oppdatert | Sensor | Tidspunkt for siste vellykkede sjekk |

### Attributter

Binary sensoren (`binary_sensor.nodvarsel_aktivt_nodvarsel`) har følgende ekstra attributter:

- `alerts` – Liste over aktive varsler med `guid`, `link`, `title`, `description`, `updated`
- `alert_count` – Antall aktive varsler
- `source` – Kilde-URL
- `attribution` – Datakilde-attribusjon

## Eksempel: Automasjon

Send varsling til telefonen når det sendes et nødvarsel:

```yaml
automation:
  - alias: "Nødvarsel – Send varsling"
    trigger:
      - platform: state
        entity_id: binary_sensor.nodvarsel_aktivt_nodvarsel
        to: "on"
    action:
      - action: notify.mobile_app_telefon
        data:
          title: "Nødvarsel!"
          message: >
            {{ state_attr('binary_sensor.nodvarsel_aktivt_nodvarsel', 'alerts')[0].title }}
          data:
            url: >
              {{ state_attr('binary_sensor.nodvarsel_aktivt_nodvarsel', 'alerts')[0].link }}
```

## Konfigurasjon

| Innstilling | Standard | Beskrivelse |
|---|---|---|
| Oppdateringsintervall | 90 sek | Hvor ofte RSS-feeden sjekkes (30–600 sek) |

Oppdateringsintervallet kan endres etter installasjon via **Innstillinger → Enheter og tjenester → Nødvarsel → Konfigurer**.

## Datakilde

Denne integrasjonen henter data fra [nødvarsel.no](https://www.nodvarsel.no), en tjeneste levert av:
- **Direktoratet for samfunnssikkerhet og beredskap (DSB)**
- **Politiet**
- **Sivilforsvaret**

## Lisens

MIT License – se [LICENSE](LICENSE) for detaljer.
