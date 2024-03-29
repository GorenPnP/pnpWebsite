/*
import in html:
	<script src="{% static 'res/js/axios.min.js' %}" type='text/javascript'></script>
	<script src="{% static 'base/js/ajax.js' %}"></script>


In js:

	post(data:dict, success:function, error:function)
	get(data, success, error)
*/

function reaction(data, status=200) {

	if (Object.keys(data).indexOf("message") !== -1 && !!data["message"])
		alert(data['message'])

	else if (Object.keys(data).indexOf("url") !== -1 && data["url"])
		window.location.href = data['url']


	if (status === 404)
		window.location.href = '/404'
}


document.addEventListener("DOMContentLoaded", () => {

	axios.defaults.baseURL = document.location.href;
	axios.defaults.headers.common['X-CSRFToken'] = document.getElementsByName('csrfmiddlewaretoken')[0].value;
	axios.defaults.headers.post['Content-Type'] = 'application/json';
})

function get(data, success, error) { send("get", data, success, error)}
function post(data, success, error) { send("post", data, success, error)}


function send(method='get', data, success, error) {
	success = success || reaction;
	error = error || reaction;

	axios.defaults.method = method
	axios({ data: data })
		.then((response) => {
			// handle success
			success(response.data)
		})
		.catch((err) => {
			error(err)
			/*

			TODO: REVIEW THIS, commented out because of /quiz/sp_modules

			// handle error
			//error(err);
			if (err.response) {
				// The request was made and the server responded with a status code
				// that falls out of the range of 2xx
				reaction(err.response.data, err.response.status);
			} else if (err.request) {
				// The request was made but no response was received
				// `error.request` is an instance of XMLHttpRequest
				reaction({}, 418)
				console.log(err.request);
			} else {
				// Something happened in setting up the request that triggered an Error
				console.log('Error', err.message);
			}
			console.log(err.config);
			*/
		});
}
