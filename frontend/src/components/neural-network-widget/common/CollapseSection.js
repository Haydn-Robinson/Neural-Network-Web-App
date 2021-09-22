import { FaCaretDown, FaCaretUp } from 'react-icons/fa'

function CollapseSection({title, toggleCollapse, expanded}) {

  return (
    <div>
      <button
        className='collapse'
        style={{ backgroundColor: expanded ? 'RoyalBlue' : 'LightBlue'}}
        onClick={toggleCollapse}
      >
      <span><h3>{title}</h3>{expanded ? <FaCaretUp/> : <FaCaretDown/>}</span>
    </button>
    </div>
  )
}

export default CollapseSection
