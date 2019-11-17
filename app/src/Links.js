import React from 'react'
import moment from 'moment'
import AwesomeDebouncePromise from 'awesome-debounce-promise';

import APIClient from './client'

import './Links.css'

class Links extends React.Component {
    constructor() {
        super()
        this.state = {
            limit: 10,
            links: []
        }

        this.handleLimitChanged = this.handleLimitChanged.bind(this)
    }

    fetchLinks() {
        this.setState({fetching: true})
        this.apiClient.links(this.state.limit).then((data) =>
            this.setState({...this.state, links: data, fetching: false})
        )
    }

    async componentDidMount() {
        this.apiClient = new APIClient()
        this.handleLimitChangedDebounced = AwesomeDebouncePromise(() => {
            this.fetchLinks()
        }, 500).bind(this)
        this.fetchLinks()
    }

    handleLimitChanged = async e => {
        let limit = e.target.value
        this.setState({ limit: limit })
        const result = await this.handleLimitChangedDebounced(limit)
        this.setState({ links: result })
    }

    renderLinks(links) {
        if (!links) {
            return (<h1>No links :(</h1>)
        }

        let linkItems = links.map((link) => {
            let createdRelative = moment(link.date)
            return (
                <div key={link.id} className="LinksItem">
                    <span>
                    <a href={link.link} rel={link.link}>
                        {link.title}
                    </a>
                    </span>
                    <span> by {link.by}</span>
                    <b title={createdRelative.format()}> {createdRelative.fromNow()}</b>
                </div>
            )
        })
        return (
            <div className="LinksWrapper">
                {linkItems}
            </div>
        )
    }
    render() {
        return (
            <div className="Links">
                <div className="Links--Control">
                    <form>
                        <label>
                            HOW MANY ITEMS TO SHOW
                            <input type="text" name="items_to_show" onChange={this.handleLimitChanged} />
                        </label>
                    </form>
                </div>
                <h1>Links</h1>
                { this.state.fetching ? "Fetching links..." : this.renderLinks(this.state.links)}
            </div>
        )
    }
}
export default Links