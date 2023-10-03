{% load custom_filters %}
<!--<div  name="a{{node.id}}" style="padding: 2px;margin: 1px">-->
    <div class="parent-div" style="padding: 4px;margin: 2px;">
      <!-- <a  name="a{{node.id}}" style="font-size:x-small;padding: 0px;margin: 0px;"></a>-->
      <span>
        <fieldset name="a{{node.id}}" style="border: none;border-radius:6px; padding: 5px;margin: 4px;">
            <span class="text-muted font-weight-bold">
          {% if node.parent.id %}&triangleright;{% endif %} 
          {% if not request.user.is_anonymous %} 
          <a  href="{% url 'user_info' node.created_by %}"><b>         
            {{ node.created_by }}
          </b></a>
          {% else %}
          <span style="color:darkblue"><b>
            {{ node.created_by }}
          </b></span>
          {% endif %}
        </span>&bull;
        <span style="font-size: small;" title="{{ node.created_on|date:'d.m.Y' }} {{ node.created_on|date:'H:i' }}">
        {% if display_time %} 
          {{ node.created_on|date:"d.m.Y" }} {{ node.created_on|date:"H:i" }}
        {% else %}
          {{ node.created_on|timediff }}
        {% endif %} 
        </span> 
        {% if node.parent.id %} 
        <span title="{{ comment.created_on|date:'d.m.Y' }} {{ comment.created_on|date:'H:i' }} : {{node.parent.content}}" style="text-align: left; font-size: small;">&bull;&nbsp;odpověd na <a href="#a{{node.parent.id}}"><b>{{node.parent.created_by}}</b>
          {% if display_time %} 
            z {{ node.parent.created_on|date:"d.m.Y" }} {{ node.parent.created_on|date:"H:i" }}
          {% else %}
            {{ node.parent.created_on|timediff }}  
          {% endif %}  
          </a>
        </span>
        {% endif %}    
            <p style="padding: 2px;margin: 3px; ">
              {{ node.content|safe }}
            </p>
        </fieldset>
      </span>
        <div class="parent-div"  style="padding:1px; margin:4px; margin-top:3px; display:flex; justify-content: space-between;"">
          <span>
            {% include "comments/comment_rate.html" %}  <!-- rate -->
          </span>
          <span>
          {% if not thread_id and node.replies_count %} <!-- vlákno --> 
              <a class="a-xsmall-button" title="zobrazit vlákno" href="{% url 'comments_thread' diskuse_id node.root_id %}">&nbsp;<b>&equiv;</b>&nbsp;</a>&nbsp;
          {% endif %} 
          <a class="a-xsmall-button" title="sdílet přispěvek" href="{% url 'comment_copy_link' node.id %}">&nbsp;sdílet&nbsp;</a>
          {% if thread_id %}
          <!--<a class="a-xsmall-button" title="volby přispěvku" href="{% url 'options_comment_thread' diskuse_id node.id thread_id %}">&nbsp;<b></b>možnosti&nbsp;&blacktriangledown;&nbsp;</a>-->
          {% else %}
          <!--<a class="a-xsmall-button" title="volby přispěveku" href="{% url 'options_comment' diskuse_id node.id %}">&nbsp;<b></b>možnosti&nbsp;&blacktriangledown;&nbsp;</a>-->
          {% endif %}
          {% if not request.user.is_anonymous and request.user.username|lower == node.created_by|lower %}
            {% if thread_id %}
                &nbsp;<a class="a-xsmall-button" href="{% url 'reply_comment_thread' 'edit' diskuse_id node.id thread_id%}">&nbsp;editovat&nbsp;</a>
            {% else %}
                &nbsp;<a class="a-xsmall-button" href="{% url 'reply_comment' 'edit' diskuse_id node.id%}">&nbsp;editovat&nbsp;</a>
            {% endif %}
            &nbsp;<a class="a-xsmall-button" href="{% url 'delete_comment' node.id%}">&nbsp;<span style="color:red">&cross;</span>&nbsp;smazat&nbsp;</a>
          {% else %}  
            {% if thread_id %}            
            &nbsp;<a  class="a-xsmall-button" href="{% url 'reply_comment_thread' 'reply' diskuse_id node.id thread_id %}">&nbsp;<b>reagovat&nbsp;&blacktriangleright;</b>&nbsp;</a>
            {% else %}
            &nbsp;<a  class="a-xsmall-button" href="{% url 'reply_comment' 'reply' diskuse_id node.id%}">&nbsp;<b>reagovat&nbsp;&blacktriangleright;</b>&nbsp;</a>
            {% endif %}
          {% endif %}
          </span>
        </div>
        {% if options_comment == node.id %}
        <div id="o{{node.id}}" class="parent-div"  style="border:0px solid #010000;border-radius:4px;background-color:lightgray;padding:6px; margin:4px; margin-top:3px; display:flex; justify-content: space-between;"">
        {% else %}
        <div id="o{{node.id}}" hidden>
          {% endif %}
          <span>
            &nbsp;<a class="a-xsmall-button" title="sdílet přispěvek" href="{% url 'comment_copy_link' node.id %}">&nbsp;sdílet&nbsp;</a>&nbsp;&nbsp;
            <a class="a-xsmall-button" title="nahlásit přispěvek" href="{% url 'comments' diskuse_id %}">&nbsp;! nahlásit příspěvek&nbsp;</a>&nbsp;&nbsp;
            {% if not request.user.is_anonymous and request.user.username|lower == node.created_by|lower %}
            {% if thread_id %}
                &nbsp;<a class="a-xsmall-button" href="{% url 'reply_comment_thread' 'edit' diskuse_id node.id thread_id%}">&nbsp;editovat&nbsp;</a>&nbsp;&nbsp;
            {% else %}
                &nbsp;<a class="a-xsmall-button" href="{% url 'reply_comment' 'edit' diskuse_id node.id%}">&nbsp;editovat&nbsp;</a>&nbsp;&nbsp;
            {% endif %}
            &nbsp;<a class="a-xsmall-button" href="{% url 'delete_comment' node.id%}">&nbsp;<span style="color:red">&cross;</span>&nbsp;smazat&nbsp;</a>&nbsp;&nbsp;
          {% endif %}  
          </span>
          <span>
            <a class="a-xsmall-button" title="zavřít" href="{% url 'comments' diskuse_id %}">&nbsp;X&nbsp;</a>&nbsp;
          </span>
        </div>
        {% if not request.user.is_anonymous %} 
          {% if reply_comment == node.id %}
          <div id="{{node.id}}" style="padding: 0px;margin: 0px;">
          {% else %}
          <div id="{{node.id}}" hidden>
          {% endif %}
          {% if operation == 'edit' %}
          {% if thread_id %}
          <form  style="padding: 0px;margin: 0px;" method="POST" action="{% url 'reply_comment_thread' 'edit'  diskuse_id node.id thread_id%}">{% csrf_token %} 
              <br>
              {{ form_reply.as_table }}
              <br> 
              <button type="submit" class="a-xsmall-button" name="edit">&nbsp;Uložit&nbsp;</button>
              <button type="submit" class="a-xsmall-button" name="cancel">&nbsp;Zrušit&nbsp;</button>
          </form>
          {% else %}
          <form  style="padding: 0px;margin: 0px;" method="POST" action="{% url 'reply_comment' 'edit' diskuse_id node.id %}">{% csrf_token %} 
            <br>
            {{ form_reply.as_table }}
            <br> 
            <button type="submit" class="a-xsmall-button" name="edit">&nbsp;Uložit&nbsp;</button>
            <button type="submit" class="a-xsmall-button" name="cancel">&nbsp;Zrušit&nbsp;</button>
          </form>
          {% endif %}
          {% else %} <!-- operation='reply' -->
          {% if thread_id %}
            <form  method="POST" action="{% url 'reply_comment_thread' 'reply' diskuse_id node.id thread_id%}">{% csrf_token %} 
              <br>
              {{ form_reply.as_table }} 
              <br>
              <button type="submit" class="a-xsmall-button" name="reply">&nbsp;Uložit&nbsp;</button>
              <button type="submit" class="a-xsmall-button" name="cancel">&nbsp;Zrušit&nbsp;</button>
            </form>
          {% else %}
            <form  method="POST" action="{% url 'reply_comment' 'reply' diskuse_id node.id %}">{% csrf_token %} 
              <br>
              {{ form_reply.as_table }} 
              <br>
              <button type="submit" class="a-xsmall-button" name="reply">&nbsp;Uložit&nbsp;</button>
              <button type="submit" class="a-xsmall-button" name="cancel">&nbsp;Zrušit&nbsp;</button>
            </form>
          {% endif %}
          {% endif %} <!-- operation -->
        {% endif %}
   </div>
{% if node.replies_count and not node.parent and not thread_id and not auto_show_all_replies and root_id != node.id %}
<div class="horizontal-line"  >
  <span id="p{{node.id}}" style="cursor: pointer;text-align: center;" class="line-text"><a class="a-small-bold-hover" href="#a'{{node.id}}'" style="font-size:small;cursor: pointer;" onclick="zobrazitElement('p'+'{{node.id}}', 'ul' + '{{node.id}}', 'a'+ '{{node.id}}' );">&nbsp;&blacktriangledown;&nbsp;zobrazit reakce&nbsp;&blacktriangledown;</a></span>
</div>
{% endif %}
</div>
