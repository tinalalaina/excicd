interface SkeletonProps {
  lines?: number
}

const Skeleton = ({ lines = 3 }: SkeletonProps) => {
  return (
    <div className="skeleton">
      {Array.from({ length: lines }).map((_, index) => (
        <span key={index} className="skeleton-line" />
      ))}
    </div>
  )
}

export default Skeleton
