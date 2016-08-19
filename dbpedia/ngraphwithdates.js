/*
A script used to create an ngraph.graph object from a .dot
of CauseGraph data and annotate it with birth years.
*/

var fs = require('fs');
var dot = require('ngraph.fromdot');
var ser = require('ngraph.serialization/json')
var birthyears = require('/Users/Shared/causegraph/birth_years.json')

var graphstr = fs.readFileSync('/Users/Shared/causegraph/prototypes/prototype-graphml/influences_shortlabels.dot', 'utf8')
var graph1 = dot(graphstr)

graph1.forEachNode(function(node){
    if(node['id'] in birthyears){
        node.data = birthyears[node['id']]
    } else {
        console.log('error with', node['id'])
}})

graph_json = ser.save(graph1)
fs.writeFileSync('ngraph_with_dates.json', graph_json, 'utf8')
