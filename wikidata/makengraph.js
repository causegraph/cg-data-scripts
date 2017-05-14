fs = require('fs')
dot = require('ngraph.fromdot')
ser = require('ngraph.serialization/json')
start_years = require('./wd_years.json')
createLayout = require('ngraph.offline.timelayout')
save = require('ngraph.tobinary')

graphstr = fs.readFileSync('nxcg.dot', 'utf-8')
graph = dot(graphstr)

year_present_count = 0
total = 0
graph.forEachNode(function (node) {
    if (node['id'] in start_years) {
        node.data = start_years[node['id']]
        year_present_count += 1
    }
    total += 1
})
console.log("makengraph: start dates present for " + year_present_count + "/" +
    total)

graph_json = ser.save(graph)
fs.writeFileSync('ngraph_with_dates.json', graph_json, 'utf8')
layout = createLayout(graph)
layout.run()
save(graph)
