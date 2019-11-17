import axios from 'axios'

const API_BASE_URL = '/api'

const client = axios.create({
    baseURL: API_BASE_URL,
    json: true
})

class APIClient {
    links(size) {
        if (!size) {
            size = 10
        }
        return this.do('get', '/links', {
            params: { size: size }
        })
    }

    async do(method, resource, kwargs) {
        return client({
            method,
            url: resource,
            ...kwargs
        }).then(res => {
            return res.data ? res.data : {'error': 'no_response'}
        })
    }
}

export default APIClient