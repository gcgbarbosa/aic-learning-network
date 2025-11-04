/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_870893133")

  // add field
  collection.fields.addAt(2, new Field({
    "cascadeDelete": false,
    "collectionId": "pbc_1548785595",
    "hidden": false,
    "id": "relation428131712",
    "maxSelect": 1,
    "minSelect": 0,
    "name": "chatbot_id",
    "presentable": false,
    "required": false,
    "system": false,
    "type": "relation"
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_870893133")

  // remove field
  collection.fields.removeById("relation428131712")

  return app.save(collection)
})
