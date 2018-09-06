# vlass2caom2
Application to generate a CAOM2 observation from VLASS FITS files

# Accessing VLASS data from CADC

Please note that the VLASS metadata is currently on a development server. The UI and TAP queries work against this server. The process of ingesting the VLASS metadata into the production servers has begun and once completed, we will advise you of the change in URLs for the UI and TAP services. The development server version of the metadata will be deleted shortly afterwards. This change does not affect access to the files.

All VLASS metadata and data at CADC is public, therefore there is no need to log in to access the CADC query or data retrieval services.

Documentation:
  - Browser UI: http://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/doc/advancedsearch/
  - TAP: http://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/doc/tap/
  - CLI for direct file download: http://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/doc/data/

Development services (available now):
  - The browser UI is available here: http://sc2.canfar.net/search/. Queries and downloading of files are fully functional.
  - The URL of the TAP (Table access protocol) service: http://sc2.canfar.net/sc2tap.
  - An example VLASS TAP synchronous query (note adding sync to the URL): curl http://sc2.canfar.net/sc2tap/sync -n -L -d "LANG=ADQL&FORMAT=TSV" --data-urlencode "QUERY=select count(*) as numObservations from caom2.Observation where collection='VLASS'"
  - One could also use the Topcat tool (http://www.star.bris.ac.uk/~mbt/topcat/) to query.

CLI for accessing files directly (available now):
  - Common command line tools such as curl and wget can be used to retrieve VLASS files.
  - Cutout operations as described on the documentation page are also supported for VLASS data.
  - A VLASS example: curl -O -L http://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/data/pub/VLASS/VLASS1.1.ql.T03t30.J194539-313000.10.2048.v1.I.iter1.image.pbcor.tt0.subim.fits

Production services (available soon):
  - The browser UI will be available here: http://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/search/.
  - The URL of the TAP (Table access protocol) service will be: http://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/tap.
