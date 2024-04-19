import xbmc
import random

uas = ['Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:52.0) Gecko/20100101 Firefox/52.0','Mozilla/5.0 (iPad; CPU OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) CriOS/30.0.1599.12 Mobile/11A465 Safari/8536.25 (3B92C18B-D9DE-4CB7-A02A-22FD2AF17C8F)','Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 950) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Mobile Safari/537.36 Edge/13.10586','Mozilla/5.0 (Linux; Android 5.0.2; LG-V410/V41020c Build/LRX22G) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/34.0.1847.118 Safari/537.36','Mozilla/5.0 (Linux; Android 7.0; Pixel C Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.98 Safari/537.36','Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30.']


ua = (random.choice(uas))

tvparams = {
  "operationName": "avod",
  "variables": {},
  "query": "fragment ChannelParts on epgItem {  title  episodeTitle  rating  language  contentType  description  startTime  endTime  __typename}query avod {  reelCollection(id: \"livetv-collection-id\") {    name    reels(paging: {number: 1, size: 30}) {      id      name      items(paging: {number: 1, size: 50}) {        ... on LiveTvReelItem {          id          name          urlId          url          source          description          genres          images {            mono            stylized            __typename          }          type          onNow {            id            ...ChannelParts            __typename          }          onNext {            ...ChannelParts            __typename          }          __typename        }        __typename      }      __typename    }    __typename  }}"
}


false = False

vodparams = {
  "operationName": "getCollection",
  "variables": {
    "id": "free-on-demand",
    "reelsPageId":  '',
    "includePhysicalPrice": false,
    "storeId": 0
  },
  "query": "query getCollection($id: ID!, $reelsPageId: ID, $includePhysicalPrice: Boolean!, $storeId: Long!) {\n  reelCollection(id: $id) {\n    id: collectionId\n    name\n    queryId\n    reelsPage(id: $reelsPageId) {\n      id\n      nextPageId\n      reels {\n        id\n        name\n       attributes {\n          browseLabel\n          browsePath\n          __typename\n        }\n        items(paging: {number: 1, size: 50}) {\n          ... on Product {\n            name\n            mediaFormats: titleDetails {\n              mediumTypeGroup\n              mediumType\n              physicalPrices(filter: {storeId: $storeId, purchaseType: BUY}) @include(if: $includePhysicalPrice) {\n                price\n                purchaseType\n                __typename\n              }\n              __typename\n            }\n            id: productGroupId\n            name\n            productPagePath: productPage\n            genres\n            type\n            images {\n              boxArtVertical\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
}
