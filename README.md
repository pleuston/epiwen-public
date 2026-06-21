# epiwen-public — Epiwen public corpus

The **default, public corpus** read by the Epiwen app
(`pleuston/epiwen`, https://pleuston.github.io/epiwen/).

It holds stone-inscription **rubbings** and their **holding-institution
authorities** (Harvard-Yenching, UC Berkeley EAL, IHP, EFEO), all from public
sources. Person/place authorities and the bibliography are the common, always-on
reference layer in the private `epiwen-data` backend; the Stone Sutras sites and
inscriptions are an opt-in private corpus there.

## Layout

```
collections/rubbings/
  *.xml                 rubbing records (TEI-EpiDoc; IIIF manifests for deep zoom)
  authority/*.xml       holding-institution authority records (MADS)
  authority-index.json  index of the institution authorities
  _package.json         { "title": "Public corpus (rubbings)" }
```

The Epiwen app loads this as the default corpus; images stream live from each
institution's IIIF service.
