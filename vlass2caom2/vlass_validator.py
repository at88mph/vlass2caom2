# -*- coding: utf-8 -*-
# ***********************************************************************
# ******************  CANADIAN ASTRONOMY DATA CENTRE  *******************
# *************  CENTRE CANADIEN DE DONNÉES ASTRONOMIQUES  **************
#
#  (c) 2019.                            (c) 2019.
#  Government of Canada                 Gouvernement du Canada
#  National Research Council            Conseil national de recherches
#  Ottawa, Canada, K1A 0R6              Ottawa, Canada, K1A 0R6
#  All rights reserved                  Tous droits réservés
#
#  NRC disclaims any warranties,        Le CNRC dénie toute garantie
#  expressed, implied, or               énoncée, implicite ou légale,
#  statutory, of any kind with          de quelque nature que ce
#  respect to the software,             soit, concernant le logiciel,
#  including without limitation         y compris sans restriction
#  any warranty of merchantability      toute garantie de valeur
#  or fitness for a particular          marchande ou de pertinence
#  purpose. NRC shall not be            pour un usage particulier.
#  liable in any event for any          Le CNRC ne pourra en aucun cas
#  damages, whether direct or           être tenu responsable de tout
#  indirect, special or general,        dommage, direct ou indirect,
#  consequential or incidental,         particulier ou général,
#  arising from the use of the          accessoire ou fortuit, résultant
#  software.  Neither the name          de l'utilisation du logiciel. Ni
#  of the National Research             le nom du Conseil National de
#  Council of Canada nor the            Recherches du Canada ni les noms
#  names of its contributors may        de ses  participants ne peuvent
#  be used to endorse or promote        être utilisés pour approuver ou
#  products derived from this           promouvoir les produits dérivés
#  software without specific prior      de ce logiciel sans autorisation
#  written permission.                  préalable et particulière
#                                       par écrit.
#
#  This file is part of the             Ce fichier fait partie du projet
#  OpenCADC project.                    OpenCADC.
#
#  OpenCADC is free software:           OpenCADC est un logiciel libre ;
#  you can redistribute it and/or       vous pouvez le redistribuer ou le
#  modify it under the terms of         modifier suivant les termes de
#  the GNU Affero General Public        la “GNU Affero General Public
#  License as published by the          License” telle que publiée
#  Free Software Foundation,            par la Free Software Foundation
#  either version 3 of the              : soit la version 3 de cette
#  License, or (at your option)         licence, soit (à votre gré)
#  any later version.                   toute version ultérieure.
#
#  OpenCADC is distributed in the       OpenCADC est distribué
#  hope that it will be useful,         dans l’espoir qu’il vous
#  but WITHOUT ANY WARRANTY;            sera utile, mais SANS AUCUNE
#  without even the implied             GARANTIE : sans même la garantie
#  warranty of MERCHANTABILITY          implicite de COMMERCIALISABILITÉ
#  or FITNESS FOR A PARTICULAR          ni d’ADÉQUATION À UN OBJECTIF
#  PURPOSE.  See the GNU Affero         PARTICULIER. Consultez la Licence
#  General Public License for           Générale Publique GNU Affero
#  more details.                        pour plus de détails.
#
#  You should have received             Vous devriez avoir reçu une
#  a copy of the GNU Affero             copie de la Licence Générale
#  General Public License along         Publique GNU Affero avec
#  with OpenCADC.  If not, see          OpenCADC ; si ce n’est
#  <http://www.gnu.org/licenses/>.      pas le cas, consultez :
#                                       <http://www.gnu.org/licenses/>.
#
#  $Revision: 4 $
#
# ***********************************************************************
#

import io
import logging

from datetime import datetime
from urllib import parse as parse

from astropy.io.votable import parse_single_table

from cadcutils import net
from cadctap import CadcTapClient
from caom2pipe import manage_composable as mc

from vlass2caom2 import APPLICATION, scrape, VlassName

__all__ = ['validate']


def read_file_list_from_archive(config):
    ad_resource_id = 'ivo://cadc.nrc.ca/ad'
    agent = '{}/{}'.format(APPLICATION, '1.0')
    subject = net.Subject(certificate=config.proxy_fqn)
    client = net.BaseWsClient(resource_id=ad_resource_id,
                              subject=subject, agent=agent, retry=True)
    query_meta = "SELECT fileName FROM archive_files WHERE " \
                 "archiveName = '{}'".format(config.archive)
    data = {'QUERY': query_meta, 'LANG': 'ADQL', 'FORMAT': 'csv'}
    logging.debug('Query is {}'.format(query_meta))
    try:
        response = client.get('https://{}/ad/sync?{}'.format(
            client.host, parse.urlencode(data)), cert=config.proxy_fqn)
        if response.status_code == 200:
            # ignore the column name as the first part of the response
            artifact_files_list = response.text.split()[1:]
            return artifact_files_list
        else:
            raise mc.CadcException('Query failure {!r}'.format(response))
    except Exception as e:
        raise mc.CadcException('Failed ad content query: {}'.format(e))


def read_list_from_caom():
    config = mc.Config()
    config.get_executors()
    query = "SELECT A.uri FROM caom2.Observation AS O " \
            "JOIN caom2.Plane AS P ON O.obsID = P.obsID " \
            "JOIN caom2.Artifact AS A ON P.planeID = A.planeID " \
            "WHERE O.collection='VLASS'"
    subject = net.Subject(certificate=config.proxy_fqn)
    tap_client = CadcTapClient(
        subject, resource_id='ivo://cadc.nrc.ca/ams/cirada')
    buffer = io.BytesIO()
    tap_client.query(query, output_file=buffer)
    temp = parse_single_table(buffer).to_table()
    return [ii.decode().replace('ad:VLASS/', '') for ii in temp['uri']]


def read_list_from_nrao():
    start_date = datetime.strptime('01Jan1990 00:00', scrape.PAGE_TIME_FORMAT)
    vlass_list, vlass_date = scrape.build_file_url_list(start_date)
    temp = [VlassName(url=ii).file_name for ii in vlass_list]
    result = list(set(temp))
    return result


def _log_list(compare_this, to_this, message):
    missing = [ii.strip() for ii in compare_this if ii not in to_this]
    if len(missing) > 0:
        logging.error('{} missing {}.'.format(len(missing), message))
        logger = logging.getLogger()
        if logger.level == logging.DEBUG:
            logging.debug('\n'.join(ii for ii in missing))
    else:
        logging.info('Found all {}.'.format(message))


def validate():
    caom_list = read_list_from_caom()
    vlass_list = read_list_from_nrao()
    _log_list(caom_list, vlass_list, 'entries from CAOM collection at NRAO')
    _log_list(vlass_list, caom_list, 'files from NRAO in VLASS archive')
    return vlass_list, caom_list
