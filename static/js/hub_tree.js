$(function()
{
	var options = {
		placeholderCss: {'background-color': '#ff8'},
		hintCss: {'background-color':'#bbf'},
        onChange: function( cEl )
        {
            console.log( 'onChange' );
        },
        complete: function( cEl )
        {
            console.log( 'complete' );
        },
		isAllowed: function( cEl, hint, target )
		{
			// Be carefull if you test some ul/ol elements here.
			// Sometimes ul/ols are dynamically generated and so they have not some attributes as natural ul/ols.
			// Be careful also if the hint is not visible. It has only display none so it is at the previouse place where it was before(excluding first moves before showing).
			if( target.data('module') === 'hub')
			{
				hint.css('background-color', '#ff9999');
				return false;
			}
			else
			{
				hint.css('background-color', '#99ff99');
				return true;
			}
		},
		opener: {
            active: true,
            as: 'html',  // if as is not set plugin uses background image
            close: '<i class="fa fa-minus-square fa-1"></i>',  // or 'fa-minus c3',  // or './imgs/Remove2.png',
            open: '<i class="fa fa-plus-square fa-1"></i>',  // or 'fa-plus',  // or'./imgs/Add2.png',
            openerCss: {
                'display': 'inline-block',
                //'width': '18px', 'height': '18px',
                'float': 'left',
                'margin-left': '-35px',
                'margin-right': '5px',
                //'background-position': 'center center', 'background-repeat': 'no-repeat',
                'font-size': '1.1em'
            }
		},
		ignoreClass: 'clickable'
	};

	$('#sTree2').sortableLists( options );

	$('.clickable').on('click', function(e)	{ alert('Click works fine! IgnoreClass stopped onDragStart event.'); });


});