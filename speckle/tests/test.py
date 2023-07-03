import pytest


@pytest.fixture
def meta():
    #from speckle.graphql import queries, query
    #_ = queries().general_meta()
    #_ = query(_)
    # = the following
    _ = {'streams':
         {'items': [{'id': '59e5e3c6a8', 'name': 'Pritoni', 'branches': 
                     {'items': [{'id': 'd1d34b78a1', 
                                 'name': 'main', 
                                 'createdAt': '2023-01-05T18:44:09.984Z', 
                                 'commits': {'items':
                                              [{'id': '83eb9c4180', 'referencedObject': 'c7070593520e21704fc6599fb579ae6a', 'createdAt': '2023-04-21T15:03:51.935Z'},
                                                {'id': '7bbee74d78', 'referencedObject': 'f445dd5c1e963f683cab931269a71ad3', 'createdAt': '2023-04-21T14:17:12.444Z'},
                                                {'id': '130aeb7b09', 'referencedObject': 'f76f6e257e1c4a01541217274a1f65cf', 'createdAt': '2023-04-21T13:43:28.583Z'},
                                                {'id': '32622d63f3', 'referencedObject': 'f76f6e257e1c4a01541217274a1f65cf', 'createdAt': '2023-04-21T12:48:02.973Z'}, 
                                                {'id': 'dc7af142e7', 'referencedObject': 'f5f2a699d96cb5eca77d879f5dfc33ea', 'createdAt': '2023-01-05T18:50:54.431Z'}, 
                                                {'id': '13f50fd4ca', 'referencedObject': '8c3680583ad72e149b9590e9d0bda5af', 'createdAt': '2023-01-05T18:47:58.841Z'},
                                                {'id': '4dba4397fc', 'referencedObject': '3ed9adaff4c5d2e99174fc89e468a55b', 'createdAt': '2023-01-05T18:45:15.102Z'}]}},
                                {'id': '8e8a907d59', 'name': 'electrical',
                                 'createdAt': '2023-06-15T22:19:56.619Z',
                                 'commits': {'items':
                                              [{'id': '63ffe62712', 'referencedObject': 'f95c4e2bf3b1cd393fdb880e3b06125d', 'createdAt': '2023-06-16T17:55:44.438Z'},
                                                {'id': '530f648454', 'referencedObject': '699693afc44b6c40dcfb415cea5b8576', 'createdAt': '2023-06-16T15:59:30.095Z'},
                                                {'id': 'c9af8d9640', 'referencedObject': '2264b53855ec6eadac1bd8030c9770a1', 'createdAt': '2023-06-16T15:56:57.102Z'},
                                                {'id': 'd5452f867a', 'referencedObject': '983a7928d18000c442952b5d5b5fcb87', 'createdAt': '2023-06-16T15:04:35.264Z'}, 
                                                {'id': '22eba6d953', 'referencedObject': 'b22d12781311d8d0535ee8a1e4cac91a', 'createdAt': '2023-06-16T15:01:21.034Z'},
                                                {'id': 'd618c83aa5', 'referencedObject': 'e0cc516a36b54fde2159cfa8397fb644', 'createdAt': '2023-06-16T04:05:03.804Z'}, 
                                                {'id': '5b71bbd76b', 'referencedObject': '6d245f197729950ddab07de0a55baf14', 'createdAt': '2023-06-16T03:34:31.341Z'}, 
                                                {'id': '6b6dac398c', 'referencedObject': '0aa0f39768fa990568ba2d3d2f9ec863', 'createdAt': '2023-06-16T03:33:15.161Z'}, 
                                                {'id': '3450a018c3', 'referencedObject': '99aaa9b5c439dd0e8b3a7a141a4e219e', 'createdAt': '2023-06-16T03:30:41.267Z'},
                                                {'id': '66a25e9fe2', 'referencedObject': '2c3bf498c5104ea193429a104b1ffff5', 'createdAt': '2023-06-15T22:20:41.309Z'}]}},
                                {'id': '0b7adcf91d', 'name': 'test', 
                                 'createdAt': '2023-06-20T19:03:53.591Z',
                                 'commits': {'items': [{'id': 'adcbb72f87', 'referencedObject': 'd60ce5c67d64221de21d8f0c735d80c1', 'createdAt': '2023-06-20T19:09:51.031Z'}]}}]}},
                     {'id': 'bf7685a6aa', 'name': 'lbnl-bldg59', 'branches':
                      {'items': [{'id': '19cd9a7b15', 'name': 'main',
                                  'createdAt': '2023-01-17T22:51:20.883Z',
                                  'commits': {'items':
                                               [{'id': 'b31e0f394d', 'referencedObject': '8f388d876aece1d11ab7ca0280b16d40', 'createdAt': '2023-01-18T15:09:07.088Z'},
                                                {'id': 'ac7269c8af', 'referencedObject': '5175f34aa088c418feabf8e1e5efc429', 'createdAt': '2023-01-17T23:30:59.906Z'}]}}]}}, 
                    {'id': '1fed8e620e', 'name': 'proto-medoffice', 'branches':
                     {'items': [{'id': 'd45dafded5', 'name': 'main', 'createdAt': '2023-01-17T23:34:58.533Z',
                                 'commits': {'items': [{'id': 'c602faa902', 'referencedObject': '6520cc7ad7bac91c2c48dad11c561ed3', 'createdAt': '2023-01-18T15:14:41.437Z'},
                                                       {'id': '2e04c6fd91', 'referencedObject': '168c66fc218e24fadee358ddf509b7ca', 'createdAt': '2023-01-17T23:50:33.022Z'}]}}]}},
                    {'id': '5bf2239c71', 'name': 'neea-medoffice', 'branches':
                     {'items': [{'id': '835c1cbfe2', 'name': 'main', 'createdAt': '2022-12-13T22:24:43.633Z',
                                 'commits':{'items': 
                                            [{'id': '99e3dfdd6a', 'referencedObject': 'efcf5ceb023c007822667520324e0a0e', 'createdAt': '2023-01-18T15:17:59.021Z'},
                                              {'id': 'fff8440af4', 'referencedObject': '6027e114e1fdea8633298a30ceaceede', 'createdAt': '2022-12-13T22:29:40.453Z'}]}}]}},
                    {'id': '316586b660', 'name': 'Error', 'branches': 
                     {'items': [{'id': 'f7fb102079', 'name': 'main', 'createdAt': '2022-12-13T22:46:31.869Z',
                                 'commits': {'items': [{'id': '3b990880b2', 'referencedObject': '37c11d7537a358eb35970e09b3837aa8', 'createdAt': '2022-12-13T22:50:16.327Z'},
                                                       {'id': '95a53efca0', 'referencedObject': 'f948c72c9b2388f562eff47a7a61b1cf', 'createdAt': '2022-12-13T22:48:43.700Z'}]}}]}}]}}
    return _


def test_rdf(meta):
    from speckle.meta import rdf


    _ = {
            'id':'o1', # ok maybe just take this id as speckle and reinterpret as schema.org/id
            'Outside': 'sdf',
            '@inside': [
                {'id': 'i1', 
                'p': 3},
                [{'referencedId': 'rid', 'speckle_type': 'reference' }],
                {'referencedId': 'rid2', 'speckle_type': 'reference' },
            ]
        }
    _ = sample_json()
    _ = remove_at(_)
    _ = id_(_) 
    _ = contextualize(_) # context after other stuff
    #return _
    from pyld import jsonld as lj
    _ = lj.flatten(_, )#contextualize({})['@context'])
    _ = lj.to_rdf(_, options=NS(format='application/n-quads').__dict__ ) #close to flatten
    import rdflib
    _ = rdflib.Graph().parse(data=_, format='nquads')
    return _
    #_ = lj.expand(_, )# NS(graph=True).__dict__ )
    #_ = lj.flatten(_, contextualize({})['@context']  ) # creates @graph
    return _


