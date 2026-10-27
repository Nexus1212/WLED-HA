// Test the actual Function node code from the shipped Node-RED example.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const flow = JSON.parse(fs.readFileSync(path.join(__dirname, '../examples/node-red-arbeitszimmer-ready.json'), 'utf8'));
const ids = new Set(flow.map(n => n.id));
assert.equal(ids.size, flow.length);
for (const n of flow) for (const wire of n.wires || []) for (const id of wire) assert(ids.has(id));
const route = new Function('msg', flow.find(n => n.id === 'wled-ready-filter').func);
const ready = new Function('msg', flow.find(n => n.id === 'wled-ready-response').func);
const data = {entity_id: 'light.wled_2_segment_1', request_id: 'request-123', segment_id: 1};
for (const payload of [{event: data}, {data}, data]) {
    const message = route({payload});
    assert.deepEqual(message.wled_request, {entity_id: data.entity_id, request_id: data.request_id});
    // Service output may replace payload; our saved request must survive.
    message.payload = {result: 'service completed'};
    const response = ready(message);
    assert.deepEqual(response.payload, {
        event: 'wled_segment_turn_on_ready',
        data: {entity_id: data.entity_id, request_id: data.request_id},
    });
}
assert.equal(route({payload: {event: {...data, entity_id: 'light.other'}}}), null);
assert.equal(route({}), null);
assert.equal(ready(route({payload: {event: {entity_id: data.entity_id}}})), null);
assert.equal(ready({}), null);
assert.equal(ready({wled_request: {...data, request_id: ''}}), null);
const relay = flow.find(n => n.type === 'api-call-service');
assert.equal(relay.action, 'switch.turn_on');
assert.deepEqual(relay.entityId, ['switch.wled_netzteil_2']);
assert.equal(flow.find(n => n.type === 'server-events').eventType, 'wled_segment_turn_on_requested');
assert.equal(flow.find(n => n.type === 'ha-fire-event').event, 'wled_segment_turn_on_ready');
console.log('Node-RED routing, saved request IDs, reply payload and wiring verified.');
