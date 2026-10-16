"""Scenario after Discogs release 38282688 (Henry Threadgill Zooid – Cut You Where You Was): 10 tracks,
two recording sessions in the notes, two studios, musicians credited for the whole release."""
import harness as H

NOTES_TWO_DAYS = ('Tracks 1 to 5 recorded June 25, 2025 at Brooklyn Recording, Brookly, NY\n'
                  'Tracks 6 to 10 recorded June 23 and 24, 2025 at Scholes Street Studio, New York, NY')
NOTES_SEPARATE = ('Tracks 1 to 5 recorded June 25, 2025 at Brooklyn Recording, Brookly, NY\n'
                  'Tracks 6 to 10 recorded June 23 and 27, 2025 at Scholes Street Studio, New York, NY')


def setup(notes=NOTES_TWO_DAYS):
    H.TITLES[:] = [f'Piece {i}' for i in range(1, 11)]
    H.REC[:] = [H.uid('bbbbbbbb', i) for i in range(1, 11)]
    H.ARTISTS.update({3101: (H.uid('dddddddd', 101), 'Liberty Ellman'), 3102: (H.uid('dddddddd', 102), 'Henry Threadgill'),
                      3103: (H.uid('dddddddd', 103), 'Jose Davila')})
    H.COMPANIES.update({1101: ('place', H.uid('eeeeeeee', 101), 'Brooklyn Recording'),
                        1102: ('place', H.uid('eeeeeeee', 102), 'Scholes Street Studio')})
    H.MB_EXTRA.clear()
    H.PERSONAL_PUBLISHERS[:] = []

    def release():
        ex = lambda name, role, i, tracks='': {'name': name, 'anv': '', 'role': role, 'tracks': tracks, 'id': i, 'join': ''}
        return {
            'id': H.DISCOGS_ID, 'title': 'Cut You Where You Was', 'country': 'US', 'year': 2025, 'notes': notes,
            'artists': [{'name': 'Henry Threadgill Zooid', 'id': 2999, 'anv': '', 'role': '', 'join': ''}],
            'labels': [], 'series': [],
            'companies': [{'name': 'Brooklyn Recording', 'entity_type_name': 'Recorded At', 'id': 1101, 'catno': ''},
                          {'name': 'Scholes Street Studio', 'entity_type_name': 'Recorded At', 'id': 1102, 'catno': ''}],
            'extraartists': [ex('Liberty Ellman', 'Acoustic Guitar', 3101), ex('Henry Threadgill', 'Alto Saxophone', 3102),
                             ex('Jose Davila', 'Tuba', 3103, '6 to 10')],
            'tracklist': [{'position': str(i + 1), 'title': t, 'type_': 'track', 'duration': '5:00', 'extraartists': []}
                          for i, t in enumerate(H.TITLES)],
        }
    H.discogs_release = release
    if 9108 not in H.ATTRS:
        H.attr(9108, 'tuba', 14, 14)
        H.LINKED['link_attribute_type']['9108'] = H.ATTRS[9108]
