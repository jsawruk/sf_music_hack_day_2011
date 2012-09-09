var apiswf = null;

//the global callback object
var callback_object = {};

callback_object.ready = function ready() {
  // Called once the API SWF has loaded and is ready to accept method calls.

  // find the embed/object element
  apiswf = $('#apiswf').get(0);

  apiswf.rdio_startFrequencyAnalyzer({
   frequencies: '10-band',
   period: 100
 })
}
