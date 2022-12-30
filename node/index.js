const { Client } = require("@notionhq/client")
require('dotenv').config();

const notion = new Client({ auth: process.env.notion_secret })
const databaseId = process.env.db_id

console.log(process.argv)
