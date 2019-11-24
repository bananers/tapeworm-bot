import React from 'react'
import moment from 'moment'
import AwesomeDebouncePromise from 'awesome-debounce-promise';
import { List, Form, Header, Divider } from 'semantic-ui-react'

import './Links.css'

class Links extends React.Component {
    constructor(props) {
        super()
        this.linksAPI = limit => props.apiClient.links(limit)
        this.debouncedLinksAPI = AwesomeDebouncePromise(this.linksAPI, 500)

        this.state = {
            limit: 10,
            links: [],
            fetching: true,
        }

        this.handleLimitChanged = this.handleLimitChanged.bind(this)
    }

    async fetchLinks() {
        return this.linksAPI(this.state.limit)
    }

    async componentDidMount() {
        const results = await this.fetchLinks()
        this.setState({...this.state, links: results.results, fetching: false})
    }

    handleLimitChanged = async e => {
        let limit = e.target.value
        this.setState({ limit: limit, fetching: true, links: [] })
        const result = await this.debouncedLinksAPI(limit)

        this.setState({ ...this.state, links: result.results, fetching: false})
    }

    renderLinks(links) {
        if (links.length === 0) {
            return (<h1>No links :(</h1>)
        }

        let linkItems = links.map((link) => {
            let createdRelative = moment(link.date)
            return (
                <div key={link.id} className="LinksItem" style={{padding: "8px"}}>
                <List.Item>
                    <List.Content>
                        <List.Header>
                            <a href={link.link} rel={link.link} style={{fontSize: "20px"}}>
                                {link.title}
                            </a>
                        </List.Header>
                        <List.Description>
                            By {link.by} {createdRelative.fromNow()} <b title={createdRelative.format()}> </b>
                        </List.Description>
                    </List.Content>
                </List.Item>
                </div>
            )
        })
        return (
            <div>
                <List divided relaxed>
                    {linkItems}
                </List>
            </div>
        )
    }
    render() {
        return (
            <div className="Links">
                <div className="Links--Control">
                    <Form>
                    <Form.Group inline>
                        <label><Header as='h3'>HOW MANY ITEMS TO SHOW</Header></label>
                        <Form.Input size='mini' type="text" name="items_to_show" onChange={this.handleLimitChanged}/>
                    </Form.Group>
                    </Form>
                    <Divider />
                </div>
                { this.state.fetching
                    ? "Fetching links..."
                    : this.renderLinks(this.state.links)
                }
            </div>
        )
    }
}
export default Links