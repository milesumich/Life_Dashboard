const { Client } = require("@notionhq/client")
require('dotenv').config();


let day_str = process.argv[2]
day_str = day_str.replace(/'/g, '"')
day_obj = JSON.parse(day_str)

const notion = new Client({ auth: process.env.notion_secret })
const databaseId = process.env.db_id

async function start() {
  const response = await notion.pages.create({
    parent: {
      database_id: databaseId,
    },
    properties: {
      "Week Day": {
        title: [
          {
            type: "text",
            text: {
              content: day_obj["Week Day"],
            },
          },
        ],
      },
      "Water (fl oz)": {
        number: day_obj["Water (fl oz)"],
      },
      "Sleep (Hrs)": {
        number: day_obj["Sleep (Hrs)"],
      },
      "Exercise (Pct)": {
        number: day_obj["Exercise (Pct)"],
      },
      "Date": {
        "date": {
          "start": day_obj["Date"],
          "end": day_obj["Date"]
        }
      }
    }
  })


  console.log(response)
}

start()

