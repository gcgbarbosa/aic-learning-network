/// <reference path="../pb_data/types.d.ts" />
migrate((app) => {
  const collection = app.findCollectionByNameOrId("pbc_3508435212")

  // update field
  collection.fields.addAt(1, new Field({
    "autogeneratePattern": "",
    "hidden": false,
    "id": "text1523469548",
    "max": 0,
    "min": 0,
    "name": "system_message",
    "pattern": "",
    "presentable": false,
    "primaryKey": false,
    "required": true,
    "system": false,
    "type": "text"
  }))

  // update field
  collection.fields.addAt(2, new Field({
    "cascadeDelete": false,
    "collectionId": "pbc_1548785595",
    "hidden": false,
    "id": "relation428131712",
    "maxSelect": 1,
    "minSelect": 0,
    "name": "chatbot_id",
    "presentable": false,
    "required": true,
    "system": false,
    "type": "relation"
  }))

  // update field
  collection.fields.addAt(3, new Field({
    "cascadeDelete": false,
    "collectionId": "pbc_3535628324",
    "hidden": false,
    "id": "relation280719904",
    "maxSelect": 1,
    "minSelect": 0,
    "name": "interaction_settings_id",
    "presentable": false,
    "required": true,
    "system": false,
    "type": "relation"
  }))

  return app.save(collection)
}, (app) => {
  const collection = app.findCollectionByNameOrId("pbc_3508435212")

  // update field
  collection.fields.addAt(1, new Field({
    "autogeneratePattern": "",
    "hidden": false,
    "id": "text1523469548",
    "max": 0,
    "min": 0,
    "name": "system_message",
    "pattern": "",
    "presentable": false,
    "primaryKey": false,
    "required": false,
    "system": false,
    "type": "text"
  }))

  // update field
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

  // update field
  collection.fields.addAt(3, new Field({
    "cascadeDelete": false,
    "collectionId": "pbc_3535628324",
    "hidden": false,
    "id": "relation280719904",
    "maxSelect": 1,
    "minSelect": 0,
    "name": "interaction_settings_id",
    "presentable": false,
    "required": false,
    "system": false,
    "type": "relation"
  }))

  return app.save(collection)
})
