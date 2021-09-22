import PropTypes from 'prop-types'

function Button({colour, text, onClick, disabled}) {

  return (
    <button
      className='btn'
      style={{ backgroundColor: disabled ? 'gainsboro' : colour }}
      onClick={onClick}
      disabled = {disabled ? true : false}
    >
      {text}
    </button>
  )
}

Button.defaultProps = {
  disabled: false
}

Button.propTypes = {
  text: PropTypes.string,
  colour: PropTypes.string,
  onClick: PropTypes.func,
  disabled: PropTypes.bool
}

export default Button
