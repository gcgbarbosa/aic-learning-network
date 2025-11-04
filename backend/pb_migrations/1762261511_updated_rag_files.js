/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_870893133")

  // update field
  collection.fields.addAt(1, new Field({
    "cascadeDelete": false,
    "collectionId": "pbc_3508435212",
    "hidden": false,
    "id": "relation3480340361",
    "maxSelect": 1,
    "minSelect": 0,
    "name": "chatbot_settings_id",
    "presentable": false,
    "required": true,
    "system": false,
    "type": "relation"
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_870893133")

  // update field
  collection.fields.addAt(1, new Field({
    "cascadeDelete": false,
    "collectionId": "pbc_3508435212",
    "hidden": false,
    "id": "relation3480340361",
    "maxSelect": 1,
    "minSelect": 0,
    "name": "chatbot_settings_id",
    "presentable": false,
    "required": false,
    "system": false,
    "type": "relation"
  }))

  return app.save(collection)
})
