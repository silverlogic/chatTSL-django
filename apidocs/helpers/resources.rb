require 'middleman-syntax'

module Resources
  module Helpers

    STATUSES ||= {
      200 => '200 OK',
      201 => '201 Created',
      202 => '202 Accepted',
      204 => '204 No Content',
      205 => '205 Reset Content',
      301 => '301 Moved Permanently',
      302 => '302 Found',
      307 => '307 Temporary Redirect',
      304 => '304 Not Modified',
      401 => '401 Unauthorized',
      403 => '403 Forbidden',
      404 => '404 Not Found',
      405 => '405 Method not allowed',
      409 => '409 Conflict',
      422 => '422 Unprocessable Entity',
      500 => '500 Server Error',
      502 => '502 Bad Gateway'
    }

    def json(key)
      hash = get_resource(key)
      hash = yield hash if block_given?
      Middleman::Syntax::Highlighter.highlight(JSON.pretty_generate(hash), 'json').html_safe
    end

    def get_resource(key)
      hash = case key
        when Hash
          h = {}
          key.each { |k, v| h[k.to_s] = v }
          h
        when Array
          key
        else Resources.const_get(key.to_s.upcase)
      end
      hash
    end

    def text_html(response, status, head = {})
      hs = headers(status, head.merge('Content-Type' => 'text/html'))
      res = CGI.escapeHTML(response)
      hs + %(<pre class="body-response"><code>) + res + "</code></pre>"
    end

  end

  AUTH_TOKEN ||= {
    token: "lkja8*lkajsd*lkjas;ldkj8asd;kJASd811"
  }

  USER ||= {
    id: 1,
    email: 'john@gmail.com',
    is_email_confirmed: false,
    new_email: '',
    is_new_email_confirmed: false,
  }

end

include Resources::Helpers
