fs = require('fs')
dot = require('ngraph.fromdot')
createLayout = require('ngraph.offline.layout')
save = require('ngraph.tobinary')

graphstr = fs.readFileSync('opentree.dot', 'utf-8')
graph = dot(graphstr)
save(graph)
